import streamlit as st

st.set_page_config(page_title="AI Homework Grader", layout="centered")
st.title("AI Homework Grader")

uploaded = st.file_uploader(
    "Upload your homework (PDF / Image / Text)",
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

if uploaded is None:
    st.info("Upload a file to start grading.")
else:
    st.success(f"Uploaded: {uploaded.name}")

    if uploaded.type == "text/plain":
        text = uploaded.read().decode("utf-8", errors="ignore")
        st.subheader("Preview")
        st.text_area("Content", text, height=250)

    st.write("File received. Next step: grading + feedback.")
