from pathlib import Path
import re

import streamlit as st


st.set_page_config(
    page_title="Grading Dashboard",
    page_icon="📝",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
IMG_ROOT = BASE_DIR / "img"
OCR_ROOT = BASE_DIR / "ocr"
RES_ROOT = BASE_DIR / "res"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
GROUPED_TASK_TYPES = ("Lnko", "Lineáris kongruencia", "Polinom lnko")
FLAT_TASK_TYPES = ("diof", "szimkong", "tobbgyok")
TASK_TYPES = GROUPED_TASK_TYPES + FLAT_TASK_TYPES


def natural_key(path_or_name):
    name = path_or_name.name if isinstance(path_or_name, Path) else path_or_name
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", name)
    ]


def find_text(folder, stem):
    for suffix in (".txt", ".md"):
        path = folder / f"{stem}{suffix}"
        if path.is_file():
            return path
    return None


def list_images(folder):
    return sorted(
        (
            path for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=natural_key,
    )


def format_ocr_math(text):
    def display_math(formula):
        return f"\n\n$$\n{formula.strip()}\n$$\n\n"

    # Ha az egész OCR-válasz egy csupasz aligned blokk.
    if re.fullmatch(
        r"\\begin\{aligned\}.*?\\end\{aligned\}",
        text.strip(),
        flags=re.DOTALL,
    ):
        return display_math(text)
    
    # LaTeX blokk: \[ ... \]
    text = re.sub(
        r"\\\[(.*?)\\\]",
        lambda match: display_math(match[1]),
        text,
        flags=re.DOTALL,
    )

    # Szövegközi LaTeX: \( ... \)
    text = re.sub(
        r"\\\((.+?)\\\)",
        lambda match: f"${match[1]}$",
        text,
    )

    # Sima [ ... ] csak akkor képlet, ha önálló sor és van benne matematikai jel.
    def format_bracketed_line(match):
        formula = match[1].strip()
        if "$" not in formula and re.search(r"[=^_<>≤≥≡→]|\\[A-Za-z]+", formula):
            return display_math(formula)
        return match[0]

    return re.sub(
        r"(?m)^[ \t]*\[([^\n]+)\][ \t]*$",
        format_bracketed_line,
        text,
    )


def render_text(path, missing_message, *, format_math=False):
    if path is None:
        st.info(missing_message)
        return

    text = path.read_text(encoding="utf-8", errors="ignore")
    if format_math:
        text = format_ocr_math(text)
    st.markdown(text)


def render_image(path, missing_message):
    if path is None:
        st.info(missing_message)
        return

    st.image(str(path), use_container_width=True)


st.sidebar.title("Szűrés")

available_models = (
    sorted((path.name for path in OCR_ROOT.iterdir() if path.is_dir()), key=natural_key)
    if OCR_ROOT.is_dir()
    else []
)

if not available_models:
    st.error("Nem található modellmappa az ocr könyvtárban.")
    st.stop()

selected_model = st.sidebar.selectbox(
    "Modell",
    available_models,
    index=available_models.index("nemotron35_vl")
    if "nemotron35_vl" in available_models
    else 0,
)

selected_task_type = st.sidebar.selectbox(
    "Feladattípus",
    TASK_TYPES,
    index=TASK_TYPES.index("diof"),
)
is_flat = selected_task_type in FLAT_TASK_TYPES

images_root = IMG_ROOT / selected_task_type
ocr_root = OCR_ROOT / selected_model / selected_task_type
res_root = RES_ROOT / selected_model / selected_task_type

if not images_root.is_dir():
    st.error(f"Nem található: {images_root}")
    st.stop()

if is_flat:
    task_dirs = [images_root]
else:
    task_dirs = sorted(
        (
            path for path in images_root.iterdir()
            if path.is_dir() and path.name.lower().startswith("task")
        ),
        key=natural_key,
    )
    if not task_dirs:
        st.info("Nincs megjeleníthető feladat.")
        st.stop()

    task_options = ["Összes"] + [path.name for path in task_dirs]
    selected_task = st.sidebar.selectbox("Feladat", task_options)
    if selected_task != "Összes":
        task_dirs = [images_root / selected_task]

st.sidebar.divider()
st.sidebar.subheader("Oszlopok")

show_image = st.sidebar.checkbox("Kép", value=True)
show_ocr = st.sidebar.checkbox("OCR", value=True)
show_result = not is_flat and st.sidebar.checkbox("Értékelés", value=True)

solution_columns = [
    label
    for label, visible in (
        ("Kép", show_image),
        ("OCR", show_ocr),
        ("Értékelés", show_result),
    )
    if visible
]

if not solution_columns:
    st.warning("Legalább egy oszlopot kapcsolj be.")
    st.stop()

st.title("Grading Dashboard")
st.caption(f"Modell: {selected_model} · Feladattípus: {selected_task_type}")

for task_dir in task_dirs:
    task_name = task_dir.name
    images = list_images(task_dir)
    task_image = None
    ocr_task_dir = ocr_root
    res_task_dir = res_root

    st.header(task_name)

    if not is_flat:
        ocr_task_dir = ocr_root / task_name
        res_task_dir = res_root / task_name
        task_image = next(
            (path for path in images if path.stem.lower().startswith("task")),
            None,
        )
        task_columns = [label for label in solution_columns if label != "Értékelés"]

        if task_columns:
            with st.expander("Feladat", expanded=True):
                cols = st.columns(len(task_columns), gap="large")
                for col, label in zip(cols, task_columns):
                    with col:
                        st.markdown(f"**{label}**")
                        if label == "Kép":
                            render_image(task_image, "Nincs feladatkép.")
                        else:
                            render_text(
                                find_text(ocr_task_dir, "_task"),
                                "Nincs feladat-OCR.",
                                format_math=True,
                            )

    solution_images = [image for image in images if image != task_image]
    if not solution_images:
        st.info("Ebben a mappában nincs megoldáskép.")
        continue

    for image in solution_images:
        st.subheader(image.stem)

        cols = st.columns(len(solution_columns), gap="large")
        for col, label in zip(cols, solution_columns):
            with col:
                st.markdown(f"**{label}**")
                if label == "Kép":
                    render_image(image, "Nincs megoldáskép.")
                elif label == "OCR":
                    render_text(
                        find_text(ocr_task_dir, image.stem),
                        "Nincs OCR ehhez a képhez.",
                        format_math=True,
                    )
                else:
                    render_text(
                        find_text(res_task_dir, image.stem),
                        "Nincs értékelés ehhez a képhez.",
                    )

        st.divider()