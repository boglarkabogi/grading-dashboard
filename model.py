import os
import base64
import time
from pathlib import Path
import requests
from dotenv import load_dotenv


# ============================================================
# ALAP BEÁLLÍTÁSOK


# ============================================================
BASE_DIR = Path(__file__).resolve().parent
IMG_ROOT = BASE_DIR / "img"
OCR_ROOT = BASE_DIR / "ocr"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
load_dotenv(BASE_DIR / ".env")
TOTAL_RECOGNITION_TIME = 0.0
TOTAL_RECOGNITIONS = 0


# ============================================================
# MODELLVÁLASZTÁS


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
    "qwen":{
        "folder": "qwen",
        "name": "Qwen/Qwen2.5-VL-72B-Instruct:ovhcloud",
        "url": "https://router.huggingface.co/v1/chat/completions",
        "key": os.getenv("HF_KEY"),
    },
    "llama": {
        "folder": "nemotron35_vl",
        "name": "nvidia/nemotron-3.5-super-vl-120b-a12b",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key": os.getenv("NVIDIA_API_KEY"),
    },
}
print("\nModellek:")
model_keys = list(MODELS.keys())
for i, key in enumerate(model_keys, start=1):
    print(f"{i} - {key}")
while True:
    choice = input("Választás: ").strip()
    try:
        index = int(choice) - 1
        if 0 <= index < len(model_keys):
            model_choice = model_keys[index]
            break
    except ValueError:
        pass
    print(f"Írj be egy számot 1 és {len(model_keys)} között.")
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
    "4": "diof",
    "5": "szimkong",
    "6": "tobbgyok",
}
print("\nFeladattípus:")
for number, name in TASK_TYPES.items():
    print(f"{number} - {name}")
while True:
    task_choice = input("Választás: ").strip()
    if task_choice in TASK_TYPES:
        break
    print("Írj be egy számot 1 és 6 között.")
TASK_TYPE = TASK_TYPES[task_choice]
FLAT_TASK_TYPES = {"diof", "szimkong", "tobbgyok"}
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
    global TOTAL_RECOGNITION_TIME, TOTAL_RECOGNITIONS
    recognition_start = time.perf_counter()
    payload = {
        "model": MODEL["name"],
        "temperature": 0,
        "max_tokens": 8192 if model_choice == "dots" else 4096,
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
    if model_choice == "kimi":
        payload["reasoning_effort"] = "low"

    if MODEL["folder"] == "nemotron35_vl":
        payload["chat_template_kwargs"] = {"enable_thinking": False}

    for attempt in range(6):
        try:
            response = requests.post(
                MODEL["url"],
                headers={
                    "Authorization": f"Bearer {MODEL['key']}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=180,
            )
        except requests.exceptions.ReadTimeout:
            wait = min(10 * (2 ** attempt), 60)
            print(
                f"      Timeout. Újrapróbálás "
                f"{wait} másodperc múlva..."
            )
            time.sleep(wait)
            continue
        # Rate limit
        if response.status_code == 429:
            wait = min(10 * (2 ** attempt), 120)
            print(
                f"      Rate limit. Újrapróbálás "
                f"{wait} másodperc múlva..."
            )
            time.sleep(wait)
            continue
        response.raise_for_status()
        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content")
        finish_reason = choice.get("finish_reason")
        if content:
            recognition_time = time.perf_counter() - recognition_start
            TOTAL_RECOGNITION_TIME += recognition_time
            TOTAL_RECOGNITIONS += 1
            print(f"      Felismerési idő: {recognition_time:.2f} s")
            return content.strip()
        # Ha kifutott a tokenlimitből
        if finish_reason == "length":
            print(
                f"      Tokenlimit elfogyott "
                f"(próba {attempt + 1}/6). Újrapróbálás..."
            )
        else:
            print(
                f"      A modell üres választ adott "
                f"(próba {attempt + 1}/6). Újrapróbálás..."
            )
        time.sleep(5)
    raise RuntimeError(
        "A modell 6 próbálkozás után sem adott szöveges választ."
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


def read_solution(image: Path, task_text=None) -> str:
    if task_text is None:
        return ask_model(
            image,
            "Írd át pontosan a képen látható kézzel írt hallgatói beadást. "
            "Csak az átírást add vissza, Markdown + LaTeX formában.",
        )

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


def process_task(task_dir: Path, *, flat=False):
    print(f"\n{task_dir.name}")
    output_dir = OUTPUT_DIR if flat else OUTPUT_DIR / task_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)
    files = [
        f
        for f in task_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in EXTENSIONS
    ]
    task_image = None
    task_text = None
    if not flat:
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
# MAIN


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


def main():
    global TOTAL_RECOGNITION_TIME, TOTAL_RECOGNITIONS
    program_start = time.perf_counter()
    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Nem található: {INPUT_DIR}"
        )
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    if TASK_TYPE in FLAT_TASK_TYPES:
        process_task(INPUT_DIR, flat=True)
    else:
        task_dirs = sorted(
            [
                folder
                for folder in INPUT_DIR.iterdir()
                if folder.is_dir()
                and folder.name.lower().startswith("task")
            ],
            key=task_number,
        )
        print("\nMelyik tasktól kezdjen?")
        start_task_input = input(
            'Írd be a task számát, vagy Enter az elejétől: '
        ).strip()
        if start_task_input:
            try:
                start_task_number = int(start_task_input)
                task_dirs = [
                    task_dir
                    for task_dir in task_dirs
                    if task_number(task_dir) >= start_task_number
                ]
            except ValueError:
                print("Érvénytelen szám, indulás az elejétől.")
        print(
            f"{len(task_dirs)} task található."
        )
        for task_dir in task_dirs:
            process_task(task_dir)

    program_time = time.perf_counter() - program_start
    print("\nFeldolgozás kész.")
    print("------------------------------")
    print(f"Felismerések száma: {TOTAL_RECOGNITIONS}")
    print(f"Összes felismerési idő: {TOTAL_RECOGNITION_TIME:.2f} s")
    if TOTAL_RECOGNITIONS > 0:
        average_time = TOTAL_RECOGNITION_TIME / TOTAL_RECOGNITIONS
        print(f"Átlagos felismerési idő: {average_time:.2f} s")
    print(f"Teljes futási idő: {program_time:.2f} s")
    print("------------------------------")


if __name__ == "__main__":
    main()
