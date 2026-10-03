from pathlib import Path
import json
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
def display_image(path):
    """Kép kirajzolása; régebbi és újabb Streamlit-verzión is működik."""
    try:
        st.image(str(path), width="stretch")
    except Exception:
        st.image(str(path), use_container_width=True)


@st.cache_data(show_spinner=False)
def read_json(path_str, mtime):
    # az mtime csak a cache frissítéséhez kell (ha újrapontozod, frissüljön)
    try:
        return json.loads(Path(path_str).read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError):
        return None


def load_result(folder, stem):
    """A model.py értékelése: <stem>.json (ha van), különben None."""
    path = folder / f"{stem}.json"
    if not path.exists():
        return None
    return read_json(str(path), path.stat().st_mtime)


def render_result(data, txt_path):
    """Értékelés megjelenítése a JSON-ből; ha nincs JSON, a .txt-ből."""
    if data is None:
        render_text(txt_path, "Nincs értékelés ehhez a képhez.")
        return

    if data.get("pont") is None:
        st.error(data.get("hiba") or "Feldolgozási hiba: nincs pontszám.")
        return

    c1, c2 = st.columns(2)
    c1.metric("Pontszám", f"{data['pont']} / 1")
    c2.metric("Magabiztosság", f"{data.get('magabiztossag', '-')} / 100")

    if data.get("ocr_hiba_gyanu"):
        st.warning(
            "OCR-hiba gyanú — érdemes újra OCR-ezni."
            + (f" {data['ocr_hiba_indok']}" if data.get("ocr_hiba_indok") else "")
        )
    if data.get("ocr_7_1_gyanu"):
        st.info("Valószínű 7↔1 OCR-elírás, elfogadva.")

    st.markdown(f"**Indoklás:** {data.get('indoklas', '-')}")
    st.markdown(f"**Diák végeredménye:** {data.get('diak_vegeredmenye', '-')}")
    st.markdown(f"**Helyes megoldás:** {data.get('helyes_megoldas', '-')}")

    with st.expander("Részletek"):
        if data.get("diak_megoldasa_osszefoglalva"):
            st.markdown(f"**A diák megoldása:** {data['diak_megoldasa_osszefoglalva']}")
        if (data.get("megjegyzes") or "").strip():
            st.markdown(f"**Megjegyzés:** {data['megjegyzes']}")
        st.caption(f"Értékelő modell: {data.get('model', '-')}")

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
    "OCR-Modell",
    available_models,
)

grader_root = RES_ROOT / selected_model
available_graders = sorted(
    [p.name for p in grader_root.iterdir() if p.is_dir()],
    key=natural_key,
) if grader_root.exists() else []

selected_grader = st.sidebar.selectbox(
    "Értékelő modell",
    available_graders if available_graders else ["(nincs értékelés)"],
)
if not available_graders:
    selected_grader = None

selected_task_type = st.sidebar.selectbox(
    "Feladattípus",
    TASK_TYPES,
)

images_root = IMG_ROOT / selected_task_type
ocr_root = OCR_ROOT / selected_model / selected_task_type
res_root = (
    RES_ROOT / selected_model / selected_grader / selected_task_type
    if selected_grader else None
)

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
    f"OCR-modell: {selected_model} · "
    f"Értékelő modell: {selected_grader or '-'} · "
    f"Feladattípus: {selected_task_type}"
)

if res_root is not None and res_root.exists():
    results = []
    for td in task_dirs:
        folder = res_root / td.name
        if folder.exists():
            for jp in folder.glob("*.json"):
                d = read_json(str(jp), jp.stat().st_mtime)
                if d is not None:
                    results.append(d)
    scored = [d["pont"] for d in results if d.get("pont") is not None]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Értékelt megoldás", len(scored))
    m2.metric("Átlagpont", f"{sum(scored) / len(scored):.2f}" if scored else "-")
    m3.metric("OCR-hiba gyanú", sum(1 for d in results if d.get("ocr_hiba_gyanu")))
    m4.metric("Feldolgozási hiba", sum(1 for d in results if d.get("pont") is None))
    st.divider()

for task_dir in task_dirs:

    task_name = task_dir.name
    task_image = find_task_image(task_dir)

    ocr_task_dir = ocr_root / task_name
    res_task_dir = res_root / task_name if res_root is not None else None

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
                            display_image(value)
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
        ) if res_task_dir is not None else None

        result_data = load_result(
            res_task_dir,
            image.stem,
        ) if res_task_dir is not None else None

        title = image.stem
        if result_data and result_data.get("pont") is not None:
            title += f" — {result_data['pont']} pont"
        st.subheader(title)

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
                    display_image(image)

                elif column_name == "OCR":
                    render_text(
                        ocr_path,
                        "Nincs OCR ehhez a képhez.",
                    )

                elif column_name == "Értékelés":
                    render_text(
                        result_data,
                        result_path,
                    )

        st.divider()
