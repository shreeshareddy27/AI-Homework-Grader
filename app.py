import os
import json
import streamlit as st

# ---------- File reading helpers ----------
def extract_text_from_txt(uploaded_file) -> str:
    return uploaded_file.read().decode("utf-8", errors="ignore")

def extract_text_from_pdf(uploaded_file) -> str:
    # Text-based PDFs (not scanned) will work well with this.
    from pypdf import PdfReader
    reader = PdfReader(uploaded_file)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()

def extract_text_from_image(uploaded_file) -> str:
    from PIL import Image
    import pytesseract

    img = Image.open(uploaded_file).convert("RGB")
    text = pytesseract.image_to_string(img)
    return text.strip()

# ---------- LLM grading ----------
def grade_with_llm(student_text: str, rubric: str, max_marks: int):
    # Uses OpenAI key from Streamlit secrets or environment
    api_key = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found. Add it in Streamlit → Manage app → Settings → Secrets.")
        st.stop()

    # OpenAI SDK (v1 style)
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    system = (
        "You are an assistant that grades homework based on a rubric. "
        "Return ONLY valid JSON with keys: score, max_score, feedback, improvements, summary."
    )

    user = f"""
RUBRIC:
{rubric}

MAX SCORE: {max_marks}

STUDENT SUBMISSION (extracted text):
{student_text}

Grade strictly using the rubric.
Rules:
- score must be an integer from 0 to max_score.
- feedback: bullet-style, specific, reference what is missing/wrong.
- improvements: 3-6 actionable bullets.
- summary: 1-2 lines.
Return ONLY JSON (no markdown).
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )

    raw = resp.choices[0].message.content.strip()

    # Try to parse JSON even if model adds extra text
    try:
        return json.loads(raw)
    except Exception:
        # fallback: find first { ... } block
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start:end+1])
        raise

# ---------- UI ----------
st.set_page_config(page_title="AI Homework Grader", layout="centered")
st.title("AI Homework Grader")

st.write("Upload homework → extract text (PDF/Image/Text) → grade + feedback")

rubric = st.text_area(
    "Rubric / Answer key (paste here)",
    placeholder="Example: \n- 2 marks: correct SQL CREATE TABLE...\n- 3 marks: constraints...\n- ...",
    height=180
)

max_marks = st.number_input("Max marks", min_value=1, max_value=200, value=10, step=1)

uploaded = st.file_uploader(
    "Upload your homework (PDF / Image / Text)",
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

if not uploaded:
    st.info("Upload a file to start grading.")
    st.stop()

st.success(f"Uploaded: {uploaded.name}")

# Extract text
with st.spinner("Extracting text..."):
    extracted = ""
    try:
        if uploaded.type == "text/plain" or uploaded.name.lower().endswith(".txt"):
            extracted = extract_text_from_txt(uploaded)
        elif uploaded.type == "application/pdf" or uploaded.name.lower().endswith(".pdf"):
            extracted = extract_text_from_pdf(uploaded)
        else:
            extracted = extract_text_from_image(uploaded)
    except Exception as e:
        st.error(f"Text extraction failed: {e}")
        st.stop()

if not extracted or len(extracted.strip()) < 10:
    st.warning("I extracted very little text. If this is a scanned PDF/image, OCR might be needed (image upload works best right now).")
else:
    with st.expander("Preview extracted text"):
        st.text_area("Extracted text", extracted, height=250)

# Grade button
if st.button("Grade now"):
    if not rubric.strip():
        st.error("Please paste a rubric/answer key first.")
        st.stop()

    with st.spinner("Grading with AI..."):
        try:
            result = grade_with_llm(extracted, rubric, int(max_marks))
        except Exception as e:
            st.error(f"LLM grading failed: {e}")
            st.stop()

    st.subheader("Result")
    st.metric("Score", f"{result.get('score')}/{result.get('max_score')}")

    st.write("### Summary")
    st.write(result.get("summary", ""))

    st.write("### Feedback")
    fb = result.get("feedback", "")
    st.write(fb)

    st.write("### Improvements")
    imp = result.get("improvements", "")
    if isinstance(imp, list):
        for x in imp:
            st.write(f"- {x}")
    else:
        st.write(imp)
