# 📄 Fluentorr — AI-Powered ATS Resume Analyzer

Fluentorr is an intelligent **Resume & Job Description (JD) matching tool** that analyzes resumes, computes ATS scores, highlights missing skills, and provides **AI-driven feedback** using Google Gemini.

This project combines **FastAPI (backend)**, **Streamlit (frontend)**, and **SQLite/Postgres (data storage)** for a complete, production-ready resume intelligence system.

---

## 🚀 Features

✅ **ATS Score & JD Fit Analysis**  
Automatically evaluates how well a resume matches a given job description using NLP and semantic similarity.  

✅ **Skill Gap Detection**  
Compares resume skills vs JD requirements and highlights missing skills.  

✅ **AI Resume Coach (Gemini)**  
Uses Google Gemini to generate personalized feedback and improvement tips.  

✅ **Modern Streamlit UI**  
Sleek dashboard showing ATS score, JD similarity, missing skills, and improvement suggestions.  

✅ **Local & Cloud Deployment Ready**  
Runs locally or can be deployed for free using **Streamlit Cloud** (UI) and **Render** (backend).

---

## 🏗️ Tech Stack

| Layer | Tech |
|-------|------|
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **AI Model** | Google Gemini (via API) |
| **Database** | SQLite (default) or Postgres (on Render) |
| **Language** | Python 3.10+ |
| **Libraries** | spaCy, pdfplumber, docx2txt, scikit-learn, google-generativeai |

---

## ⚙️ Local Setup

### 1️⃣ Clone the repo
```bash
git clone https://github.com/fahimtenzel/ats-rescue.git
cd ats-rescue
