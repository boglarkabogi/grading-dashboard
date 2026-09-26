import os
import base64
import time
import json
import random
import re
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# ALAP BEÁLLÍTÁSOK
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

IMG_ROOT = BASE_DIR / "img"
OCR_ROOT = BASE_DIR / "ocr"
RES_ROOT = BASE_DIR / "res"

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

load_dotenv(BASE_DIR / ".env", override=True)


# ============================================================
# MODELLVÁLASZTÁS (OCR)
# ============================================================

MODELS = {
    "dots": {
        "folder": "dots3",
        "name": "dots-studio/dots-3-note-preview:free",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": os.getenv("OPENROUTER_API_KEY"),
    },

    "kimi": {
        "folder": "kimi3",
        "name": "moonshotai/kimi-k3",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key": os.getenv("NVIDIA_API_KEY"),
    },
}

model_choice = None
MODEL = None
TASK_TYPE = None
INPUT_DIR = None
OUTPUT_DIR = None


def choose_ocr_model():

    global model_choice, MODEL
    while True:
        model_choice = input(
            "Válassz modellt (dots/kimi): "
        ).strip().lower()

        if model_choice in MODELS:
            break

        print('Írd be: "dots" vagy "kimi".')


    MODEL = MODELS[model_choice]

    if not MODEL["key"]:
        raise RuntimeError(
            f"Nincs API kulcs beállítva ehhez: {model_choice}"
        )


# ============================================================
# FELADATTÍPUS VÁLASZTÁS
# ============================================================

TASK_TYPES = {
    "1": "Lnko",
    "2": "Lineáris kongruencia",
    "3": "Polinom lnko",
}

def choose_task_type() -> str:
    print("\nFeladattípus:")
    print("1 - Lnko")
    print("2 - Lineáris kongruencia")
    print("3 - Polinom lnko")

    while True:
        task_choice = input("Választás: ").strip()

        if task_choice in TASK_TYPES:
            break

        print("Írj be 1-et, 2-t vagy 3-at.")

    return TASK_TYPES[task_choice]

def set_ocr_paths(task_type: str):
    global TASK_TYPE, INPUT_DIR, OUTPUT_DIR

    TASK_TYPE = task_type

    INPUT_DIR = IMG_ROOT / TASK_TYPE

    OUTPUT_DIR = (
        OCR_ROOT
        / MODEL["folder"]
        / TASK_TYPE
    )


    print("\n------------------------------")
    print(f"Modell:       {MODEL['folder']}")
    print(f"Feladattípus: {TASK_TYPE}")
    print(f"Input:        {INPUT_DIR}")
    print(f"Output:       {OUTPUT_DIR}")
    print("------------------------------\n")


# ============================================================
# PROMPT
# ============================================================

SYSTEM_PROMPT = """
Matematikai kézírás-transzkripciós rendszer vagy.

Kizárólag a képen ténylegesen látható tartalmat írd át.

Ne:
- oldd meg;
- javítsd ki;
- magyarázd;
- értékeld;
- egészítsd ki;
- találj ki hiányzó tartalmat.

A matematikai kifejezéseket Markdown + LaTeX formában add vissza.
Tartsd meg a lépések sorrendjét.

A válasz kizárólag a transzkripció legyen.
"""


# ============================================================
# KÉP -> BASE64 DATA URL
# ============================================================

def image_to_data_url(path: Path) -> str:

    mime_types = {
        ".png": "image/png",
        ".webp": "image/webp",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }

    mime = mime_types[path.suffix.lower()]

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


# ============================================================
# MODELL HÍVÁSA
# ============================================================

def ask_model(image_path: Path, prompt: str) -> str:

    payload = {
        "model": MODEL["name"],
        "temperature": 0,
        "max_tokens": 4096,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_to_data_url(image_path)
                        },
                    },
                ],
            },
        ],
    }

    # Kiminek nem kell erős reasoning az OCR-hez
    if model_choice == "kimi":
        payload["reasoning_effort"] = "low"

    for attempt in range(6):

        response = requests.post(
            MODEL["url"],
            headers={
                "Authorization": f"Bearer {MODEL['key']}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=180,
        )

        if response.status_code != 429:
            response.raise_for_status()

            return (
                response.json()["choices"][0]["message"]["content"]
                .strip()
            )

        wait = min(10 * (2 ** attempt), 120)

        print(
            f"    Rate limit. "
            f"Várakozás {wait} másodperc..."
        )

        time.sleep(wait)

    raise RuntimeError(
        "A modell 6 próbálkozás után sem válaszolt."
    )


# ============================================================
# FELADAT BEOLVASÁSA
# ============================================================

def read_task(image: Path) -> str:

    return ask_model(
        image,
        """
Írd át pontosan a képen látható matematikai feladatot.
Ne oldd meg.
Csak a feladat szövegét add vissza.
""",
    )


# ============================================================
# MEGOLDÁS BEOLVASÁSA
# ============================================================

def read_solution(image: Path, task_text: str) -> str:

    return ask_model(
        image,
        f"""
A képen egy kézzel írt megoldás látható.

A hozzá tartozó feladat:

--- FELADAT ---
{task_text}
--- FELADAT VÉGE ---

A feladat csak kontextus.

Kizárólag a képen látható hallgatói megoldást írd át.
A feladat szövegét ne másold bele.
""",
    )


# ============================================================
# EGY TASK FELDOLGOZÁSA
# ============================================================

def process_task(task_dir: Path):

    print(f"\n{task_dir.name}")

    output_dir = OUTPUT_DIR / task_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)

    files = [
        f
        for f in task_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in EXTENSIONS
    ]

    # task_1.png, task_2.png stb.
    task_images = [
        f
        for f in files
        if f.stem.lower().startswith("task")
    ]

    if not task_images:
        print("  Nincs feladatkép.")
        return

    task_image = task_images[0]

    print(f"  Feladat: {task_image.name}")

    task_text = read_task(task_image)

    (output_dir / "_task.txt").write_text(
        task_text,
        encoding="utf-8",
    )

    solution_images = sorted(
        f
        for f in files
        if f != task_image
    )

    print(
        f"  {len(solution_images)} megoldás"
    )

    for image in solution_images:

        print(f"    {image.name}")

        try:
            text = read_solution(
                image,
                task_text,
            )

            output_file = (
                output_dir
                / f"{image.stem}.txt"
            )

            output_file.write_text(
                text,
                encoding="utf-8",
            )

        except Exception as e:
            print(f"      Hiba: {e}")

        time.sleep(2)


# ============================================================
# OCR FUTTATÁS
# ============================================================

def task_number(path: Path):

    try:
        return int(
            path.name.lower()
            .replace("task", "")
            .strip()
        )

    except ValueError:
        return 999999


def ocr_main():

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Nem található: {INPUT_DIR}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    task_dirs = sorted(
        [
            folder
            for folder in INPUT_DIR.iterdir()
            if folder.is_dir()
            and folder.name.lower().startswith("task")
        ],
        key=task_number,
    )

    print(
        f"{len(task_dirs)} task található."
    )

    for task_dir in task_dirs:
        process_task(task_dir)

    print("\nFeldolgozás kész.")

# ############################################################
#
# ÉRTÉKELÉS
#
# ############################################################

TASK_FILE = "_task.txt"            

GRADER_TEMPERATURE = 0.1
GRADER_MAX_TOKENS = 8192
REQUEST_TIMEOUT = 180            
MAX_RETRIES = 6
DEFAULT_RPM = 30                     

ALLOWED_PONT_VALUES = (0, 0.25, 0.5, 0.75, 1)


# ============================================================
# ÉRTÉKELŐ MODELLEK
# ============================================================

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

GRADER_MODELS = {
    "deepseek": {
        "folder": "deepseek-v4-flash",
        "name": "deepseek-ai/deepseek-v4-flash-0731",
        "url": NVIDIA_URL,
        "key": os.getenv("NVIDIA_API_KEY"),
    },
    "kimi": {
        "folder": "kimi3",
        "name": "moonshotai/kimi-k3",
        "url": NVIDIA_URL,
        "key": os.getenv("NVIDIA_API_KEY"),
        "temperature": 1, 
    },
}


# ============================================================
# PROMPT
# ============================================================

GRADER_SYSTEM_PROMPT = (
    "Matematika-beadandót pontozol. Megkapod a FELADATOT és egy diák OCR-ozott "
    "(esetleg zajos) megoldását. Először magad határozd meg a feladat helyes megoldását, "
    "majd döntsd el, hogy a diák megoldása mennyire helyes, és indokold. Ha a kapott "
    "szöveg maga értelmezhetetlen (OCR-halandzsa, nincs valódi megoldás), azt KÜLÖN "
    "jelezd — ne keverd össze azzal, hogy a diák elszámolta.\n\n"
    "FONTOS: a pontozás alapjáról: a köztes sorok tökéletlen OCR-ből származnak, ezért NE "
    "vonj le pontot a köztes lépések apró számolási vagy leírási hibáiért, hacsak a "
    "MÓDSZER egésze nem nyilvánvalóan rossz. A pont fő alapja: (a) helyes-e a végső "
    "eredmény, és (b) a helyes módszert használta-e a diák.\n\n"
    "A `pont` csak az alábbi öt érték egyike lehet: 0, 0.25, 0.5, 0.75, 1. Használd a "
    "részpontszámot, ha a megoldás részben helyes:\n"
    "- 1: helyes módszer és helyes végeredmény (akkor is, ha a levezetés OCR-zajos, vagy "
    "a végeredmény csak az algoritmusból olvasható ki).\n"
    "- 0.75: lényegében helyes, csak apró hiba.\n"
    "- 0.5: részben helyes: pl. jó módszer, de elrontott végeredmény; vagy félig kész.\n"
    "- 0.25: jelentős hibák, de van benne helyes elem/gondolat.\n"
    "- 0: teljesen hibás, vagy értelmezhetetlen bemenet.\n\n"
    "A `magabiztossag` mezőben azt add meg 0-100 skálán, hogy mennyire vagy magabiztos a "
    "saját értékelésedben (a pontban és az indoklásban) — NEM azt, hogy mennyire volt "
    "olvasható a bemenet. Ha bizonytalan vagy a saját értékelésedben (pl. zajos a "
    "levezetés, nehéz eldönteni, hol hibázott a diák), adj alacsonyabb értéket.\n\n"
    "OCR-tudnivaló: a képfelismerő gyakran az 1-es számjegyet 7-esnek olvassa. Ez "
    "egyirányú: a szövegben lévő 7-es lehet valójában 1-es, de egy 1-es sosem 7-es. "
    "FONTOS: Ha egy szám csak abban tér el a feladat helyes számától, hogy 7-es áll az 1-es helyén, "
    "tekintsd OCR-elírásnak, fogadd el 1-esként, ne vonj le érte pontot, és jelezd "
    "(`ocr_7_1_gyanu = true`, plusz írd a megjegyzésbe). A fordított irányt (1-es áll a "
    "7-es helyén) NE javítsd, az valódi eltérés lehet.\n\n"
    "Az `ocr_7_1_gyanu` mezőt akkor állítsd `true`-ra, ha gyanús a 7 és az 1 összekeverése "
    "az OCR-ben — nem csak önálló számként (7 az 1 helyett), hanem összetett számokban is, "
    "például: 77 a 11 helyett, 71 a 11 helyett, vagy általában ha egy számban a 7-es ott áll, "
    "ahol 1-esnek kellene lennie. Külön figyelj erre: ha feltűnően sok a 7-es a levezetésben "
    "ÉS a diák számítása emiatt nem jön ki (a maradékok/lépések nem konzisztensek), de a "
    "7-eseket 1-esként visszaolvasva a levezetés helyessé válik, az erős jel az OCR-hibára — "
    "ilyenkor jelöld be. Az `indoklas`-ban vagy a `megjegyzes`-ben röviden írd le, mely "
    "számoknál gyanítasz 1↔7 cserét.\n\n"
    "Ha a kapott szöveg annyira zavaros vagy értelmetlen, hogy nem lehet megbízhatóan "
    "értékelni — például halandzsa jelek, egymásnak ellentmondó vagy sehová nem vezető "
    "számok, teljesen szétesett levezetés, olyan karakterek/részletek, amik matematikailag "
    "értelmezhetetlenek —, akkor állítsd az `ocr_hiba_gyanu` mezőt `true`-ra, és az "
    "`ocr_hiba_indok`-ban egy mondatban írd le, mi utal OCR-hibára. Ilyenkor is add meg a "
    "legjobb tudásod szerinti pontot, de a jelzés a fontos: az ilyen beadványt újra kell "
    "OCR-ezni, nem a diáknak visszaküldeni. Ha a szöveg rendben értelmezhető, a mező maradjon "
    "`false`.\n\n"
    "Megjegyzés: az `ocr_7_1_gyanu` és az `ocr_hiba_gyanu` mező külön szerepet tölt be. Az "
    "`ocr_7_1_gyanu` a konkrét 1↔7 cserére, az `ocr_hiba_gyanu` az általános, „ez a szöveg "
    "olvashatatlanul zavaros” esetre vonatkozik. Mindkettő lehet egyszerre `true`.\n\n"
    "A feladat bármilyen matematikai feladat lehet (pl. legnagyobb közös osztó egész számokra "
    "vagy polinomokra, lineáris kongruencia). Mindig magad oldd meg a megadott feladatot, majd "
    "értékeld a diák megoldását ugyanazon elvek szerint. Ha a végeredmény csak a "
    "levezetésből/algoritmusból olvasható ki, de a módszer és az eredmény helyes, fogadd el.\n\n"
    "A JSON string mezőiben (pl. `helyes_megoldas`, `diak_vegeredmenye`, `feladat`, `indoklas`) NE "
    "használj LaTeX-et: se `$...$`, se backslash-parancsokat (`\\in`, `\\mathbb`, `\\gcd`, `\\frac`). "
    "A matematikát írd sima szöveggel: pl. `x^2 + x + 1`, `Z_5[x]`, `gcd`, `f = x^4 + 3x^3 + ...`. "
    "A polinomokat `^` hatványjellel és sima együtthatókkal add meg.\n\n"
    "Csak JSON-t adj vissza."
)

JSON_SCHEMA_BLOCK = """\
Add vissza pontosan ezt a JSON-t (más szöveg ne legyen a válaszban):
{
  "feladat": "<a feladat szövege — ha külön meg van adva, ismételd meg; ha a diák szövegéből kell kiolvasni, akkor az>",
  "helyes_megoldas": "<a feladat helyes megoldása, amit te határoztál meg>",
  "diak_vegeredmenye": "<amit a diák végeredményként megadott; ha csak az algoritmusból olvasható ki, akkor is add meg>",
  "diak_megoldasa_osszefoglalva": "<1-3 mondat a diák levezetéséről>",
  "pont": 0,
  "indoklas": "<miért kapott/nem kapott pontot>",
  "magabiztossag": 0,
  "ertelmezheto": true,
  "ocr_7_1_gyanu": false,
  "ocr_hiba_gyanu": false,
  "ocr_hiba_indok": "<1 mondat: mi utal OCR-hibára, vagy üres>",
  "megjegyzes": "<pl. ha a bemenet volt a baj, nem a diák hibája, vagy ha 7/1 OCR-gyanú volt>"
}

Emlékeztető:
- A pontozás fő alapja a helyes MÓDSZER és a helyes VÉGEREDMÉNY. A köztes sorok apró
  OCR-hibáiért ne büntess.
- A "pont" csak 0, 0.25, 0.5, 0.75 vagy 1 lehet.
- A "magabiztossag" (0-100) a SAJÁT értékelésed magabiztossága, nem a bemenet olvashatósága.
- Az "ocr_7_1_gyanu" legyen true, ha egy 7-es számjegyet 1-esként fogadtál el OCR-hiba
  gyanúja miatt (önálló számként vagy összetett számban is).
- Az "ocr_hiba_gyanu" legyen true, ha a szöveg annyira zavaros/értelmezhetetlen, hogy nem
  lehet megbízhatóan értékelni; ilyenkor az "ocr_hiba_indok" adjon rövid indokot.
- A JSON string mezőiben NE legyen LaTeX (se `$...$`, se `\\in`, `\\mathbb`, `\\gcd`, `\\frac`
  stb.) — a matekot sima szöveggel írd (pl. `x^2 + x + 1`, `Z_5[x]`, `gcd`).
"""


def build_user_message(task_text: str | None, submission: str) -> str:
    if task_text:
        intro = f"FELADAT:\n{task_text}\n\nA diák OCR-ozott megoldása:"
    else:
        intro = (
            "A feladat szövege ÉS a diák megoldása is a lenti szövegben található. "
            "Olvasd ki a feladatot, oldd meg magad, majd értékeld a diák megoldását."
            "\n\nDiák OCR-ozott beadandója (feladat + megoldás):"
        )
    return f"{intro}\n\n---\n{submission}\n---\n\n{JSON_SCHEMA_BLOCK}"


# ============================================================
# BEMENET 
# ============================================================

def find_task_dirs(input_dir: Path) -> list[Path]:
    return sorted(
        (d for d in input_dir.iterdir()
         if d.is_dir() and d.name.lower().startswith("task")),
        key=task_number,
    )


def find_submissions(task_dir: Path) -> list[Path]:
    """A megoldások átiratai: minden .txt, kivéve a _task.txt-t."""
    return sorted(f for f in task_dir.glob("*.txt") if f.name != TASK_FILE)


def read_task_text(task_dir: Path) -> str | None:
    task_file = task_dir / TASK_FILE
    if task_file.exists():
        return task_file.read_text(encoding="utf-8", errors="ignore").strip() or None
    return None


# ============================================================
# VÁLASZ FELDOLGOZÁSA 
# ============================================================

def _first_json_object(s: str) -> str | None:
    """Az első teljes {...} blokk, zárójel-mélység számolással (stringeken belül nem számol)."""
    start = s.find("{")
    if start == -1:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start:i + 1]
    return None  # csonka válasz


def _fix_latex_backslashes(s: str) -> str:
    """Duplázza azokat a '\\'-eket, amik nem érvényes JSON-escape-ek (pl. LaTeX: \\in, \\gcd)."""
    return re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", s)


def extract_json(text: str) -> dict | None:
    """JSON-objektum kinyerése: <think> blokkok levágása, majd több jelölttel próbálkozik."""
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL).strip()
    block = _first_json_object(text)
    candidates = [block, _fix_latex_backslashes(block)] if block else []
    candidates += [text, _fix_latex_backslashes(text)]
    for cand in candidates:
        try:
            result = json.loads(cand)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
    return None


def normalize_pont(result: dict) -> None:
    """A `pont`-ot a legközelebbi megengedett értékre kerekíti (0, 0.25, 0.5, 0.75, 1)."""
    try:
        pont = float(result["pont"])
    except (KeyError, TypeError, ValueError):
        return
    result["pont"] = min(ALLOWED_PONT_VALUES, key=lambda v: abs(v - pont))


# ============================================================
# ÉRTÉKELŐ MODELL HÍVÁSA
# ============================================================

_last_call = 0.0


def _throttle(rpm: int) -> None:
    """Két kérés között legalább 60/rpm másodperc teljen el."""
    global _last_call
    wait = 60.0 / rpm - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def grader_ask_model(model: dict, user_msg: str, json_mode: bool, rpm: int) -> str:
    """Egy chat-completion hívás (OpenAI-kompatibilis végpont). Hibánál kivételt dob."""
    payload = {
        "model": model["name"],
        "temperature": model.get("temperature", GRADER_TEMPERATURE),
        "max_tokens": GRADER_MAX_TOKENS,
        "stream": False,
        "messages": [
            {"role": "system", "content": GRADER_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    _throttle(rpm)
    response = requests.post(
        model["url"],
        headers={
            "Authorization": f"Bearer {model['key']}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    message = response.json()["choices"][0]["message"]
    return (message.get("content") or message.get("reasoning_content") or "").strip()


def _retry_wait(response, attempt: int) -> float:
    """A szerver Retry-After fejléce, különben exponenciális várakozás (max. 120 s)."""
    try:
        return float(response.headers["retry-after"])
    except Exception:
        return min(10 * 2 ** (attempt - 1), 120) + random.random()


def grade_submission(model: dict, task_text: str | None, submission: str,
                     rpm: int = DEFAULT_RPM) -> tuple[dict | None, str | None]:
    """Egy megoldás pontozása. Visszaad: (eredmény dict vagy None, utolsó nyers válasz).

    Először JSON-módban kér választ; ha a modell ezt nem támogatja (400), vagy nem jön ki
    értelmes JSON, a további próbálkozások sima szöveges módban mennek.
    """
    user_msg = build_user_message(task_text, submission)
    raw, json_mode = None, True

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = grader_ask_model(model, user_msg, json_mode, rpm)
        except requests.HTTPError as e:
            status = e.response.status_code
            if status == 400 and json_mode:
                print("      JSON-mód nem támogatott, újra sima szöveggel...")
                json_mode = False
                continue
            if status in (401, 403, 404):
                # Nem átmeneti hiba: rossz kulcs, vagy a modell nem (már nem) elérhető.
                raise RuntimeError(
                    f"HTTP {status}: a '{model['name']}' modell nem érhető el."
                    f"A szerver válasza: {e.response.text[:500]}"
                ) from e
            wait = _retry_wait(e.response, attempt)
            print(f"      HTTP {status} ({attempt}. próba). Várakozás {wait:.0f} másodperc...")
            time.sleep(wait)
            continue
        except requests.RequestException as e:  # időtúllépés, kapcsolati hiba
            wait = _retry_wait(None, attempt)
            print(f"      Hálózati hiba ({attempt}. próba): {e}. Várakozás {wait:.0f} másodperc...")
            time.sleep(wait)
            continue

        result = extract_json(raw)
        if result is not None:
            normalize_pont(result)
            return result, raw

        print(f"      Nem sikerült JSON-t kinyerni ({attempt}. próba).")
        json_mode = False

    return None, raw


# ============================================================
# KIMENET
# ============================================================

def format_txt(data: dict) -> str:
    """Ember által olvasható összefoglaló."""
    lines = [
        f"Feladat: {data.get('feladat', '-')}",
        f"Helyes megoldás: {data.get('helyes_megoldas', '-')}",
        "",
        f"Diák végeredménye: {data.get('diak_vegeredmenye', '-')}",
    ]
    if data.get("diak_megoldasa_osszefoglalva"):
        lines += ["Diák megoldása (összefoglalva):", data["diak_megoldasa_osszefoglalva"]]
    lines += [
        "",
        f"Pontszám: {data.get('pont', '-')}/1",
        "Indoklás:",
        data.get("indoklas", ""),
        "",
        f"Modell magabiztossága: {data.get('magabiztossag', '-')}/100",
        f"Értelmezhető volt a bemenet: {'igen' if data.get('ertelmezheto') else 'nem'}",
    ]
    if data.get("ocr_7_1_gyanu"):
        lines += ["", "Figyelem: valószínű 7↔1 OCR-elírás, elfogadva."]
    if data.get("ocr_hiba_gyanu"):
        lines += ["", "Figyelem: OCR-hiba gyanú — érdemes újra OCR-ezni."]
        if (data.get("ocr_hiba_indok") or "").strip():
            lines.append(f"Indok: {data['ocr_hiba_indok'].strip()}")
    lines += ["", "Megjegyzés:", (data.get("megjegyzes") or "").strip() or "-"]
    return "\n".join(lines)


def save_result(out_dir: Path, stem: str, model_name: str, task_text: str | None,
                result: dict | None, raw: str | None) -> None:
    """<stem>.json + <stem>.txt mentése; hiba esetén <stem>_raw.txt a nyers válasszal."""
    if result is None:
        data = {
            "feladat": task_text or "-",
            "hiba": "A modell nem adott értelmezhető JSON választ.",
            "pont": None,
            "ertelmezheto": False,
            "magabiztossag": 0,
            "ocr_7_1_gyanu": False,
            "ocr_hiba_gyanu": False,
            "ocr_hiba_indok": "",
            "model": model_name,
        }
        txt = (f"Feladat: {task_text or '(lásd a szövegben)'}\n\n"
               "[FELDOLGOZÁSI HIBA] A modell nem adott értelmes választ.\n")
        (out_dir / f"{stem}_raw.txt").write_text(
            raw or "(a modell üres vagy hiányzó választ adott)", encoding="utf-8")
    else:
        data = {**result, "model": model_name}
        txt = format_txt(data)

    (out_dir / f"{stem}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / f"{stem}.txt").write_text(txt, encoding="utf-8")


# ============================================================
# ÉRTÉKELÉS FUTTATÁSA
# ============================================================

def output_dir_for(ocr_folder: str, model_key: str, task_type: str) -> Path:
    return RES_ROOT / ocr_folder / GRADER_MODELS[model_key]["folder"] / task_type


def grade_task_dir(task_dir: Path, out_dir: Path, model: dict,
                   rpm: int = DEFAULT_RPM, force: bool = False) -> dict:
    """Egy taskN mappa összes megoldásának pontozása. Visszaad: statisztika dict."""
    stats = {"feldolgozva": 0, "kihagyva": 0, "hiba": 0}
    print(f"\n{task_dir.name}")

    submissions = find_submissions(task_dir)
    if not submissions:
        print("  Nincs megoldás-átirat.")
        return stats

    task_text = read_task_text(task_dir)
    if task_text is None:
        print(f"  Figyelem: nincs {TASK_FILE}, a feladatot a megoldásból kell kiolvasni.")

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"  {len(submissions)} megoldás")

    for submission_file in submissions:
        stem = submission_file.stem

        if not force and (out_dir / f"{stem}.json").exists():
            stats["kihagyva"] += 1
            print(f"    {stem} ... kihagyva (már pontozva)")
            continue

        submission = submission_file.read_text(encoding="utf-8", errors="ignore").strip()
        result, raw = grade_submission(model, task_text, submission, rpm)
        save_result(out_dir, stem, model["name"], task_text, result, raw)

        if result is None:
            stats["hiba"] += 1
            print(f"    {stem} ... HIBA (nyers válasz mentve)")
        else:
            stats["feldolgozva"] += 1
            print(f"    {stem} ... pont = {result.get('pont', '-')}")

    return stats


def grade(ocr_folder: str, task_type: str, model_key: str,
          rpm: int = DEFAULT_RPM, force: bool = False) -> dict:
    """Egy OCR-kimenet (ocr/<ocr_folder>/<task_type>) teljes pontozása.

    ocr_folder : pl. "kimi3" vagy "dots3" (mappa az ocr/ alatt)
    task_type  : "Lnko", "Lineáris kongruencia" vagy "Polinom lnko"
    model_key  : a GRADER_MODELS kulcsa, pl. "deepseek"
    """
    model = GRADER_MODELS[model_key]
    if not model["key"]:
        raise RuntimeError(f"Nincs API kulcs beállítva ehhez: {model_key}")

    input_dir = OCR_ROOT / ocr_folder / task_type
    output_dir = output_dir_for(ocr_folder, model_key, task_type)
    if not input_dir.exists():
        raise FileNotFoundError(f"Nem található: {input_dir}")

    print("\n------------------------------")
    print(f"OCR-kimenet:     {ocr_folder}")
    print(f"Pontozó modell:  {model['folder']} ({model['name']})")
    print(f"Feladattípus:    {task_type}")
    print(f"Input:           {input_dir}")
    print(f"Output:          {output_dir}")
    print("------------------------------")

    task_dirs = find_task_dirs(input_dir)
    print(f"{len(task_dirs)} task található.")

    total = {"feldolgozva": 0, "kihagyva": 0, "hiba": 0}
    for task_dir in task_dirs:
        stats = grade_task_dir(task_dir, output_dir / task_dir.name, model, rpm, force)
        for k in total:
            total[k] += stats[k]

    print(f"\nPontozás kész. Feldolgozva: {total['feldolgozva']}, "
          f"kihagyva: {total['kihagyva']}, hiba: {total['hiba']}")
    return total


# ############################################################
#
# MAIN
#
# ############################################################

def ask_choice(title: str, options: dict[str, str]) -> str:
    """Interaktív választás a megadott lehetőségek közül. A választott kulcsot adja vissza."""
    print(f"\n{title}:")
    for key, label in options.items():
        print(f"{key} - {label}")
    while True:
        choice = input("Választás: ").strip()
        if choice in options:
            return choice
        print(f"Írd be valamelyiket: {', '.join(options)}.")


def choose_grader_model() -> str:
    return ask_choice(
        "Értékelő modell",
        {key: m["name"] for key, m in GRADER_MODELS.items()},
    )


def choose_ocr_folder() -> str:
    """Melyik meglévő OCR-kimenetet (ocr/ alatti mappát) értékeljük."""
    available = sorted(d.name for d in OCR_ROOT.iterdir() if d.is_dir()) \
        if OCR_ROOT.exists() else []
    if not available:
        raise FileNotFoundError(f"Nincs OCR-kimenet itt: {OCR_ROOT}")
    options = {str(i): name for i, name in enumerate(available, 1)}
    return options[ask_choice("Melyik OCR-kimenetet értékeljük", options)]


STEPS = {
    "1": "OCR (img/ -> ocr/)",
    "2": "Értékelés (ocr/ -> res/)",
    "3": "OCR, majd értékelés",
}


def main():

    step = ask_choice("Mit futtassunk", STEPS)

    if step == "1":
        choose_ocr_model()
        set_ocr_paths(choose_task_type())
        ocr_main()

    elif step == "2":
        ocr_folder = choose_ocr_folder()
        task_type = choose_task_type()
        grader_key = choose_grader_model()
        grade(ocr_folder, task_type, grader_key)

    else:
        # Minden kérdés az elején, utána felügyelet nélkül fut végig.
        choose_ocr_model()
        task_type = choose_task_type()
        grader_key = choose_grader_model()
        set_ocr_paths(task_type)
        ocr_main()
        grade(MODEL["folder"], TASK_TYPE, grader_key)

if __name__ == "__main__":
    main()