import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Feladatértékelés dashboard",
    layout="wide"
)

IMAGE_DIR = Path("images")
OCR_DIR = Path("ocr-txt")
REVIEW_FILE = Path("reviews.csv")

st.title("Feladatértékelés dashboard")

# --- Képek automatikus betöltése ---
image_records = []

for img in sorted(IMAGE_DIR.iterdir()):
    if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        image_records.append({
            "image_id": img.stem,
            "image_path": str(img)
        })

df_images = pd.DataFrame(image_records)

# --- OCR szövegek betöltése ---
demo_rows = []

for _, img_row in df_images.iterrows():
    ocr_file = OCR_DIR / f"{img_row['image_id']}.txt"

    if ocr_file.exists():
        ocr_text = ocr_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    else:
        ocr_text = ""

    demo_rows.append({
        "image_id": img_row["image_id"],
        "image_path": img_row["image_path"],
        "ocr_model": "Qwen2.5-VL-7B-Instruct",
        "ocr_text": ocr_text,
        "evaluator_model": "Értékelő modell neve",
        "evaluation_text": "Ide kerül majd az értékelő modell értékelése."
    })

df = pd.DataFrame(demo_rows)

# --- Manuális review-k betöltése ---
review_columns = [
    "image_id",
    "ocr_model",
    "numbers_match",
    "gcd_match",
    "reviewed",
    "comment"
]

if REVIEW_FILE.exists() and REVIEW_FILE.stat().st_size > 0:
    reviews_df = pd.read_csv(REVIEW_FILE)
else:
    reviews_df = pd.DataFrame(columns=review_columns)

for col in review_columns:
    if col not in reviews_df.columns:
        reviews_df[col] = False if col in ["numbers_match", "gcd_match", "reviewed"] else ""

# --- Szűrők ---
st.sidebar.header("Szűrők")

image_options = ["Összes"] + sorted(
    df["image_id"].dropna().unique().tolist()
)

selected_image = st.sidebar.selectbox("Kép", image_options)

ocr_models = ["Összes"] + sorted(
    df["ocr_model"].dropna().unique().tolist()
)

evaluator_models = ["Összes"] + sorted(
    df["evaluator_model"].dropna().unique().tolist()
)

selected_ocr_model = st.sidebar.selectbox("OCR modell", ocr_models)
selected_evaluator_model = st.sidebar.selectbox("Értékelő modell", evaluator_models)

filtered = df.copy()

if selected_image != "Összes":
    filtered = filtered[filtered["image_id"] == selected_image]

if selected_ocr_model != "Összes":
    filtered = filtered[filtered["ocr_model"] == selected_ocr_model]

if selected_evaluator_model != "Összes":
    filtered = filtered[filtered["evaluator_model"] == selected_evaluator_model]

st.caption(f"{len(filtered)} megjelenített elem")

# --- Statisztikák ---
reviewed_mask = reviews_df["reviewed"].fillna(False).astype(bool)
reviewed_df = reviews_df[reviewed_mask]

total_reviewed = len(reviewed_df)

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

def stat_text(count):
    if total_reviewed == 0:
        return "0/0 (0%)"
    return f"{count}/{total_reviewed} ({100 * count / total_reviewed:.1f}%)"

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    f"Számok egyeznek ({100 * numbers_ok / total_reviewed:.1f}%)"
    if total_reviewed else "Számok egyeznek (0%)",
    f"{numbers_ok}/{total_reviewed}"
)

col2.metric(
    f"LNKO egyezik ({100 * gcd_ok / total_reviewed:.1f}%)"
    if total_reviewed else "LNKO egyezik (0%)",
    f"{gcd_ok}/{total_reviewed}"
)

col3.metric(
    f"Mindkettő egyezik ({100 * both_ok / total_reviewed:.1f}%)"
    if total_reviewed else "Mindkettő egyezik (0%)",
    f"{both_ok}/{total_reviewed}"
)

col4.metric(
    f"Kommentelt ({100 * commented / total_reviewed:.1f}%)"
    if total_reviewed else "Kommentelt (0%)",
    f"{commented}/{total_reviewed}"
)

progress = total_reviewed / len(df) if len(df) > 0 else 0
st.progress(progress)

st.caption(
    f"Átnézve: {total_reviewed}/{len(df)} kép "
    f"({100 * progress:.1f}%)"
)

st.divider()

# --- Review feed ---
for image_id, group in filtered.groupby("image_id", sort=True):
    st.divider()

    for _, row in group.iterrows():
        col_img, col_ocr, col_review, col_eval = st.columns([1.1, 1.4, 1, 1.4])

        existing_review = reviews_df[
            (reviews_df["image_id"] == row["image_id"]) &
            (reviews_df["ocr_model"] == row["ocr_model"])
        ]

        if not existing_review.empty:
            existing_review = existing_review.iloc[0]
        else:
            existing_review = None

        with col_img:
            st.markdown(f"#### 📄 {row['image_id']}")
            st.image(row["image_path"])

        with col_ocr:
            st.markdown(f"### {row['ocr_model']}")
            st.markdown("**Felismert szöveg**")
            st.code(row["ocr_text"], language="text")

        with col_review:
            st.markdown("### Manuális review")

            numbers_match = st.checkbox(
                "Számok egyeznek",
                value=bool(existing_review["numbers_match"]) if existing_review is not None else False,
                key=f"numbers_{image_id}_{row.name}"
            )

            gcd_match = st.checkbox(
                "LNKO egyezik",
                value=bool(existing_review["gcd_match"]) if existing_review is not None else False,
                key=f"gcd_{image_id}_{row.name}"
            )

            reviewed = st.checkbox(
                "Átnézve",
                value=bool(existing_review["reviewed"]) if existing_review is not None else False,
                key=f"reviewed_{image_id}_{row.name}"
            )

            comment = st.text_area(
                "Megjegyzés",
                value=str(existing_review["comment"]) if existing_review is not None and pd.notna(existing_review["comment"]) else "",
                key=f"comment_{image_id}_{row.name}"
            )

            if st.button("Mentés", key=f"save_{image_id}_{row.name}"):
                new_review = {
                    "image_id": row["image_id"],
                    "ocr_model": row["ocr_model"],
                    "numbers_match": numbers_match,
                    "gcd_match": gcd_match,
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

        with col_eval:
            st.markdown(f"### {row['evaluator_model']}")
            st.markdown("**Értékelés**")
            st.code(row["evaluation_text"], language="text")