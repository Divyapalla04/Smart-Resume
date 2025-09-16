import streamlit as st
import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import PyPDF2
import docx

# ----------- Utility Functions -----------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

def extract_keywords(text, top_n=20):
    text = clean_text(text)
    words = [w for w in text.split() if w not in ENGLISH_STOP_WORDS and len(w) > 2]
    return [word for word, _ in Counter(words).most_common(top_n)]

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

def analyze_resume(resume_text, jd_text):
    jd_keywords = set(extract_keywords(jd_text, 30))
    resume_keywords = set(extract_keywords(resume_text, 50))

    matched = jd_keywords & resume_keywords
    missing = jd_keywords - resume_keywords

    match_percentage = (len(matched) / len(jd_keywords)) * 100 if jd_keywords else 0

    return jd_keywords, resume_keywords, matched, missing, round(match_percentage, 2)

# ----------- Streamlit UI -----------
st.title("📄 Smart Resume Keyword Analyzer")
st.write("Upload your **resume** and paste a **job description** to check keyword matching.")

uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
jd_text = st.text_area("Paste Job Description Here")

if uploaded_resume and jd_text:
    resume_text = extract_text_from_file(uploaded_resume)

    jd_keywords, resume_keywords, matched, missing, match_percentage = analyze_resume(resume_text, jd_text)

    st.subheader("📊 Results")
    st.write(f"**Match %:** {match_percentage} %")

    st.write("✅ **Matched Keywords:**", ", ".join(matched) if matched else "None")
    st.write("❌ **Missing Keywords:**", ", ".join(missing) if missing else "None")

    with st.expander("🔑 Job Description Keywords"):
        st.write(", ".join(jd_keywords))

    with st.expander("📄 Resume Keywords"):
        st.write(", ".join(resume_keywords))
