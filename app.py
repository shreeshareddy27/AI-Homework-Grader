import os
import streamlit as st
from openai import OpenAI

# --- OpenAI client ---
def get_client():
    key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        st.error("Missing OPENAI_API_KEY. Add it in Streamlit → Settings → Secrets.")
        st.stop()
    return OpenAI(api_key=key)

client = get_client()

# ===== ADD TEST BUTTON RIGHT HERE =====
st.divider()
if st.button("🔌 Test OpenAI key"):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            temperature=0,
        )
        st.success(r.choices[0].message.content)
    except Exception as e:
        st.error("OpenAI call failed:")
        st.exception(e)
st.divider()
# =====================================

# --- UI ---
st.title("AI Homework Grader")

rubric = st.text_area("Rubric / Answer key (paste here)", height=160)
max_marks = st.number_input("Max marks", min_value=1, value=10)

uploaded = st.file_uploader(
    "Upload your homework (PDF / Image / Text)",
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

grade_now = st.button("Grade now")

if uploaded and grade_now:
    st.write("File received. Grading now...")

    # TODO: extracted_text = extract_text(uploaded)
    extracted_text = "REPLACE_WITH_EXTRACTED_TEXT"

    prompt = f"""
You are an automated homework grader.

Rubric/Answer key:
{rubric}

Student submission:
{extracted_text}

Return JSON with:
score (number),
max_score (number),
summary (string),
feedback (string),
improvements (array of strings).
Score must be out of {int(max_marks)}.
"""

    with st.spinner("Grading with AI..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

    st.write(resp.choices[0].message.content)
