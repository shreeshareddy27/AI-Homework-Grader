# 📝 AI Homework Grader (Ollama)

A local-first AI homework grading application built with **Streamlit** and **Ollama**.  
Supports **PDF**, **Images (OCR)**, and **TXT** files, and returns a structured **score, summary, feedback, and improvements** based on a custom rubric.

---
Currently uses Ollama (llama3.1). Earlier experiments with other LLMs were exploratory and are no longer part of the codebase.


## ✨ Features
- 📄 Upload homework: PDF / Image / TXT
- 🔍 OCR support using Tesseract
- 🧠 Local AI grading with Ollama (llama3.1)
- 📊 Clear scoring and feedback output
- 🎨 Clean and modern Streamlit UI

---

## 🛠 Tech Stack
Python · Streamlit · Ollama · pypdf · pytesseract · Pillow · requests

---

## 🚀 Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt

### System Requirements
- Ollama (local LLM server)
- Tesseract OCR (for image text extraction)

