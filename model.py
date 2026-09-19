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
}


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

print("\nFeladattípus:")
print("1 - Lnko")
print("2 - Lineáris kongruencia")
print("3 - Polinom lnko")

while True:
    task_choice = input("Választás: ").strip()

    if task_choice in TASK_TYPES:
        break

    print("Írj be 1-et, 2-t vagy 3-at.")


TASK_TYPE = TASK_TYPES[task_choice]

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


if __name__ == "__main__":
    main()