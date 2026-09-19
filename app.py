from pathlib import Path
import re

import streamlit as st


# ============================================================
# BEÁLLÍTÁSOK
# ============================================================

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

TASK_TYPES = [
    "Lnko",
    "Lineáris kongruencia",
    "Polinom lnko",
]


# ============================================================
# SEGÉDFÜGGVÉNYEK
# ============================================================

def natural_key(path_or_name):
    text = path_or_name.name if isinstance(path_or_name, Path) else str(path_or_name)
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", text)
    ]


@st.cache_data(show_spinner=False)
def read_text(path_str):
    return Path(path_str).read_text(
        encoding="utf-8",
        errors="ignore",
    )


def find_text(folder, stem):
    """Elfogad .txt és régebbi .md fájlokat is."""
    for suffix in (".txt", ".md"):
        path = folder / f"{stem}{suffix}"
        if path.exists():
            return path
    return None


def find_task_image(task_dir):
    images = sorted(
        [
            p for p in task_dir.iterdir()
            if p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
            and p.stem.lower().startswith("task")
        ],
        key=natural_key,
    )
    return images[0] if images else None


def get_solution_images(task_dir, task_image):
    return sorted(
        [
            p for p in task_dir.iterdir()
            if p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
            and p != task_image
        ],
        key=natural_key,
    )


def render_text(path, missing_message):
    if path is None:
        st.info(missing_message)
        return

    text = read_text(str(path))

    # Az OCR és az értékelés .txt fájlban van,
    # de a tartalma lehet Markdown + LaTeX.
    st.markdown(text)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Szűrés")

available_models = sorted(
    [
        p.name for p in OCR_ROOT.iterdir()
        if p.is_dir()
    ],
    key=natural_key,
) if OCR_ROOT.exists() else []

if not available_models:
    st.error("Nem található modellmappa az ocr könyvtárban.")
    st.stop()

selected_model = st.sidebar.selectbox(
    "Modell",
    available_models,
)

selected_task_type = st.sidebar.selectbox(
    "Feladattípus",
    TASK_TYPES,
)

images_root = IMG_ROOT / selected_task_type
ocr_root = OCR_ROOT / selected_model / selected_task_type
res_root = RES_ROOT / selected_model / selected_task_type

if not images_root.exists():
    st.error(f"Nem található: {images_root}")
    st.stop()

task_dirs = sorted(
    [
        p for p in images_root.iterdir()
        if p.is_dir()
        and p.name.lower().startswith("task")
    ],
    key=natural_key,
)

if not task_dirs:
    st.info("Nincs megjeleníthető task.")
    st.stop()

task_options = ["Összes"] + [p.name for p in task_dirs]

selected_task = st.sidebar.selectbox(
    "Feladat",
    task_options,
)

if selected_task != "Összes":
    task_dirs = [
        p for p in task_dirs
        if p.name == selected_task
    ]

st.sidebar.divider()
st.sidebar.subheader("Oszlopok")

show_image = st.sidebar.checkbox(
    "Kép",
    value=True,
)

show_ocr = st.sidebar.checkbox(
    "OCR",
    value=True,
)

show_result = st.sidebar.checkbox(
    "Értékelés",
    value=True,
)

if not any([show_image, show_ocr, show_result]):
    st.warning("Legalább egy oszlopot kapcsolj be.")
    st.stop()


# ============================================================
# OLDAL
# ============================================================

st.title("Grading Dashboard")
st.caption(
    f"Modell: {selected_model} · "
    f"Feladattípus: {selected_task_type}"
)


for task_dir in task_dirs:

    task_name = task_dir.name
    task_image = find_task_image(task_dir)

    ocr_task_dir = ocr_root / task_name
    res_task_dir = res_root / task_name

    task_text = find_text(
        ocr_task_dir,
        "_task",
    )

    st.header(task_name)

    # --------------------------------------------------------
    # FELADAT
    # --------------------------------------------------------

    with st.expander("Feladat", expanded=True):

        task_parts = []

        if show_image:
            task_parts.append(("Kép", task_image))

        if show_ocr:
            task_parts.append(("OCR", task_text))

        if task_parts:
            cols = st.columns(len(task_parts), gap="large")

            for col, (title, value) in zip(cols, task_parts):
                with col:
                    st.markdown(f"**{title}**")

                    if title == "Kép":
                        if value:
                            st.image(
                                str(value),
                                use_container_width=True,
                            )
                        else:
                            st.info("Nincs feladatkép.")

                    else:
                        render_text(
                            value,
                            "Nincs feladat-OCR.",
                        )

    # --------------------------------------------------------
    # MEGOLDÁSOK
    # --------------------------------------------------------

    solution_images = get_solution_images(
        task_dir,
        task_image,
    )

    if not solution_images:
        st.info("Ehhez a feladathoz nincs megoldáskép.")
        continue

    for image in solution_images:

        ocr_path = find_text(
            ocr_task_dir,
            image.stem,
        )

        result_path = find_text(
            res_task_dir,
            image.stem,
        )

        st.subheader(image.stem)

        active_columns = []

        if show_image:
            active_columns.append("Kép")

        if show_ocr:
            active_columns.append("OCR")

        if show_result:
            active_columns.append("Értékelés")

        cols = st.columns(
            len(active_columns),
            gap="large",
        )

        for col, column_name in zip(
            cols,
            active_columns,
        ):
            with col:
                st.markdown(f"**{column_name}**")

                if column_name == "Kép":
                    st.image(
                        str(image),
                        use_container_width=True,
                    )

                elif column_name == "OCR":
                    render_text(
                        ocr_path,
                        "Nincs OCR ehhez a képhez.",
                    )

                elif column_name == "Értékelés":
                    render_text(
                        result_path,
                        "Nincs értékelés ehhez a képhez.",
                    )

        st.divider()
