import os
import json
import streamlit as st
from google import genai

# --- Gemini client ---
def get_client():
    key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        st.error("Missing GEMINI_API_KEY. Add it in Streamlit → Settings → Secrets.")
        st.stop()
    return genai.Client(api_key=key)

client = get_client()


# ----------------------------
# Test button (confirm key works)
# ----------------------------
st.divider()

if st.button("Test Gemini key"):
    try:
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Reply with exactly: OK"
        )
        st.success(resp.text)
    except Exception as e:
        st.error("Gemini call failed")
        st.exception(e)

st.divider()


# ----------------------------
# UI
# ----------------------------
st.title("AI Homework Grader")

rubric = st.text_area("Rubric / Answer key (paste here)", height=160)
max_marks = st.number_input("Max marks", min_value=1, value=10)

uploaded = st.file_uploader(
    "Upload your homework (PDF / Image / Text)",
    type=["pdf", "png", "jpg", "jpeg", "txt"],
)

grade_now = st.button("Grade now")


# ----------------------------
# Helper: parse JSON safely
# ----------------------------
def parse_json(text: str):
    text = text.strip()
    # Try direct JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If model wrapped JSON in extra text, try extracting first {...}
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


# ----------------------------
# Main grading
# ----------------------------
if uploaded and grade_now:
    st.write("File received. Grading now...")

    # TODO: Replace this with your real OCR/extraction output
    extracted_text = "REPLACE_WITH_EXTRACTED_TEXT"

    if not rubric.strip():
        st.error("Please paste a rubric / answer key.")
        st.stop()

    if not extracted_text.strip() or extracted_text == "REPLACE_WITH_EXTRACTED_TEXT":
        st.error("Extraction text is missing. Replace REPLACE_WITH_EXTRACTED_TEXT with your OCR output.")
        st.stop()

    prompt = f"""
You are an automated homework grader.

Return STRICT JSON only (no markdown, no extra text).

Schema:
{{
  "score": <number between 0 and {int(max_marks)}>,
  "max_score": {int(max_marks)},
  "summary": "<1-2 sentence overall evaluation>",
  "feedback": "<clear feedback paragraph>",
  "improvements": ["...", "..."]
}}

Rubric/Answer key:
{rubric}

Student submission:
{extracted_text}
"""

    with st.spinner("Grading with Gemini..."):
        try:
            resp = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            raw = resp.text
            result = parse_json(raw)

        except Exception as e:
            st.error("Grading failed:")
            st.exception(e)
            st.stop()

    # Display nicely
    st.success("Done")
    st.metric("Score", f'{result.get("score", "?")} / {result.get("max_score", int(max_marks))}')

    st.write("### Summary")
    st.write(result.get("summary", ""))

    st.write("### Feedback")
    st.write(result.get("feedback", ""))

    st.write("### Improvements")
    for item in result.get("improvements", []):
        st.write(f"- {item}")

    with st.expander("Show raw JSON"):
        st.code(json.dumps(result, indent=2))
