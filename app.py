import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Feladatértékelés dashboard",
    layout="wide"
)

SHOW_QWEN = True
SHOW_GPT = False
SHOW_DEEPSEEK = False
SHOW_MANUAL_REVIEW = False

TASK_OPTIONS = {
    "LNKO": "Lnko",
    "Lineáris kongruencia": "Lineáris kongruencia",
}

st.sidebar.header("Szűrők")

selected_task = st.sidebar.selectbox(
    "Feladattípus",
    list(TASK_OPTIONS.keys())
)

TASK_DIR = Path(TASK_OPTIONS[selected_task])

IMAGE_DIR = TASK_DIR / "images"
TXT_DIR = TASK_DIR / "txt"

OCR_DIR = TXT_DIR
OCR_GROUPED_DIR = TXT_DIR / "ocr-txt-grouped"
REASONING_DIR = TXT_DIR / "reasoning-txt"
DEEPSEEK_DIR = TXT_DIR / "evaluated-txt"

REVIEW_FILE = TXT_DIR / "reviews.csv"

st.title("Feladatértékelés dashboard")

# --- Képek automatikus betöltése ---
image_records = []

if not IMAGE_DIR.exists():
    st.error(f"Nem találom az images mappát: {IMAGE_DIR.resolve()}")
    st.stop()

for item in sorted(IMAGE_DIR.iterdir()):
    if item.is_dir():
        task_group = item.name

        for img in sorted(item.iterdir()):
            if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                image_records.append({
                    "task_group": task_group,
                    "image_id": img.stem,
                    "image_path": str(img)
                })

    elif item.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        image_records.append({
            "task_group": selected_task,
            "image_id": item.stem,
            "image_path": str(item)
        })

df_images = pd.DataFrame(
    image_records,
    columns=["task_group", "image_id", "image_path"]
)

# --- OCR + értékelések betöltése ---
demo_rows = []

for _, img_row in df_images.iterrows():
    image_id = img_row["image_id"]
    task_group = img_row["task_group"]

    ocr_file = OCR_DIR / f"{image_id}-ocr.txt"
    ocr_grouped_file = OCR_GROUPED_DIR / task_group / f"{image_id}-ocr.txt"
    reasoning_file = REASONING_DIR / f"{image_id}_evaluation.txt"
    deepseek_file = DEEPSEEK_DIR / f"{image_id}.txt"

    ocr_text = (
        ocr_file.read_text(encoding="utf-8", errors="ignore")
        if ocr_file.exists()
        else "Nincs Qwen OCR."
    )

    ocr_grouped_text = (
        ocr_grouped_file.read_text(encoding="utf-8", errors="ignore")
        if ocr_grouped_file.exists()
        else "Nincs grouped Qwen OCR."
    )

    evaluation_text = (
        reasoning_file.read_text(encoding="utf-8", errors="ignore")
        if reasoning_file.exists()
        else "Nincs GPT értékelés."
    )

    deepseek_text = (
        deepseek_file.read_text(encoding="utf-8", errors="ignore")
        if deepseek_file.exists()
        else "Nincs DeepSeek értékelés."
    )

    qwen_text = ocr_grouped_text if selected_task == "LNKO" else ocr_text
    qwen_title = "Qwen2.5-VL-7B-Instruct"

    demo_rows.append({
        "task_group": task_group,
        "image_id": image_id,
        "image_path": img_row["image_path"],
        "ocr_model": "Qwen2.5-VL-7B-Instruct",
        "qwen_title": qwen_title,
        "qwen_text": qwen_text,
        "evaluation_text": evaluation_text,
        "deepseek_text": deepseek_text,
    })

df = pd.DataFrame(demo_rows)

# --- Manuális review-k betöltése ---
review_columns = [
    "image_id",
    "ocr_model",
    "numbers_match",
    "gcd_match",
    "seven_one_problem",
    "reviewed",
    "comment"
]

if REVIEW_FILE.exists() and REVIEW_FILE.stat().st_size > 0:
    reviews_df = pd.read_csv(REVIEW_FILE)
else:
    reviews_df = pd.DataFrame(columns=review_columns)

for col in review_columns:
    if col not in reviews_df.columns:
        reviews_df[col] = False if col in [
            "numbers_match",
            "gcd_match",
            "seven_one_problem",
            "reviewed"
        ] else ""

# --- Szűrők ---
st.sidebar.header("Szűrők")

image_options = ["Összes"] + sorted(
    df["image_id"].dropna().unique().tolist()
)

selected_image = st.sidebar.selectbox("Kép", image_options)

# --- Review adatok összekapcsolása ---
filtered = df.merge(
    reviews_df,
    on=["image_id", "ocr_model"],
    how="left",
    suffixes=("", "_review")
)

for bool_col in ["numbers_match", "gcd_match", "seven_one_problem", "reviewed"]:
    filtered[bool_col] = filtered[bool_col].fillna(False).astype(bool)

filtered["comment"] = filtered["comment"].fillna("").astype(str)

if selected_image != "Összes":
    filtered = filtered[filtered["image_id"] == selected_image]

st.caption(f"{len(filtered)} megjelenített elem")

# --- Statisztikák ---
reviewed_mask = reviews_df["reviewed"].fillna(False).astype(bool)
reviewed_df = reviews_df[reviewed_mask]

total_reviewed = len(reviewed_df)

if total_reviewed > 0:
    numbers_ok = reviewed_df["numbers_match"].fillna(False).astype(bool).sum()
    gcd_ok = reviewed_df["gcd_match"].fillna(False).astype(bool).sum()

    both_ok = (
        reviewed_df["numbers_match"].fillna(False).astype(bool)
        &
        reviewed_df["gcd_match"].fillna(False).astype(bool)
    ).sum()

    commented = (
        reviewed_df["comment"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    seven_one_count = (
        reviewed_df["seven_one_problem"]
        .fillna(False)
        .astype(bool)
        .sum()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(f"Számok egyeznek ({100 * numbers_ok / total_reviewed:.1f}%)", f"{numbers_ok}/{total_reviewed}")
    col2.metric(f"LNKO egyezik ({100 * gcd_ok / total_reviewed:.1f}%)", f"{gcd_ok}/{total_reviewed}")
    col3.metric(f"Mindkettő egyezik ({100 * both_ok / total_reviewed:.1f}%)", f"{both_ok}/{total_reviewed}")
    col4.metric(f"Kommentelt ({100 * commented / total_reviewed:.1f}%)", f"{commented}/{total_reviewed}")
    col5.metric(f"7-es ↔ 1-es probléma ({100 * seven_one_count / total_reviewed:.1f}%)", f"{seven_one_count}/{total_reviewed}")

    progress = min(total_reviewed / len(df), 1.0) if len(df) > 0 else 0
    st.progress(progress)

    st.caption(
        f"Átnézve: {total_reviewed}/{len(df)} kép "
        f"({100 * progress:.1f}%)"
    )

    st.divider()

# --- Review feed ---
for task_group, task_df in filtered.groupby("task_group", sort=True):

    st.header(f"Task: gcd({task_group.replace('_', ', ')})")

    for image_id, group in task_df.groupby("image_id", sort=True):

        for _, row in group.iterrows():
            active_eval_columns = []

            if SHOW_GPT:
                active_eval_columns.append("gpt")

            if SHOW_DEEPSEEK:
                active_eval_columns.append("deepseek")

            if SHOW_MANUAL_REVIEW:
                top_img, top_qwen, top_review = st.columns(
                    [1.1, 1.35, 1.1]
                )
            else:
                top_img, top_qwen = st.columns(
                    [1.0, 1.3]
                )

            existing_review = reviews_df[
                (reviews_df["image_id"] == row["image_id"]) &
                (reviews_df["ocr_model"] == row["ocr_model"])
            ]

            if not existing_review.empty:
                existing_review = existing_review.iloc[0]
            else:
                existing_review = None

            with top_img:
                st.markdown(f"### 📄 {row['image_id']}")
                st.image(row["image_path"])

            with top_qwen:
                st.markdown(f"### {row['qwen_title']}")
                st.code(row["qwen_text"], language="text")

            if SHOW_MANUAL_REVIEW:
                with top_review:
                    st.markdown("### Manuális review")

                    numbers_match = st.checkbox(
                        "Számok egyeznek",
                        value=bool(existing_review["numbers_match"])
                        if existing_review is not None else False,
                        key=f"numbers_{image_id}_{row.name}"
                    )

                    gcd_match = st.checkbox(
                        "LNKO egyezik",
                        value=bool(existing_review["gcd_match"])
                        if existing_review is not None else False,
                        key=f"gcd_{image_id}_{row.name}"
                    )

                    seven_one_problem = st.checkbox(
                        "7-es 1-es probléma",
                        value=bool(existing_review["seven_one_problem"])
                        if existing_review is not None
                        else False,
                        key=f"sevenone_{image_id}_{row.name}"
                    )

                    reviewed = st.checkbox(
                        "Átnézve",
                        value=bool(existing_review["reviewed"])
                        if existing_review is not None else False,
                        key=f"reviewed_{image_id}_{row.name}"
                    )

                    comment = st.text_area(
                        "Megjegyzés",
                        value=str(existing_review["comment"])
                        if existing_review is not None and pd.notna(existing_review["comment"])
                        else "",
                        key=f"comment_{image_id}_{row.name}"
                    )

                    if st.button("Mentés", key=f"save_{image_id}_{row.name}"):
                        new_review = {
                            "image_id": row["image_id"],
                            "ocr_model": row["ocr_model"],
                            "numbers_match": numbers_match,
                            "gcd_match": gcd_match,
                            "seven_one_problem": seven_one_problem,
                            "reviewed": reviewed,
                            "comment": comment
                        }

                        reviews_df = reviews_df[
                            ~(
                                (reviews_df["image_id"] == row["image_id"]) &
                                (reviews_df["ocr_model"] == row["ocr_model"])
                            )
                        ]

                        reviews_df = pd.concat(
                            [reviews_df, pd.DataFrame([new_review])],
                            ignore_index=True
                        )

                        reviews_df.to_csv(REVIEW_FILE, index=False)
                        st.success("Mentve")

            def show_eval(model_name):
                if model_name == "gpt":
                    st.markdown("### GPT-5.5")
                    st.markdown("**Értékelés**")
                    st.code(row["evaluation_text"], language="text")

                if model_name == "deepseek":
                    st.markdown("### DeepSeek-R1-14B")
                    st.markdown("**Értékelés**")
                    st.code(row["deepseek_text"], language="text")

            st.divider()