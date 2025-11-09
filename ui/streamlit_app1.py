# ui/streamlit_app.py
import streamlit as st
import requests
import sqlite3
import pandas as pd
from pathlib import Path

API_URL = "http://127.0.0.1:8000/upload"
DB_PATH = Path("resume_results.db")

st.set_page_config(page_title="Fluentorr ATS Analyzer", layout="centered")
st.title("📄 Resume ATS Analyzer — with optional storage")

st.sidebar.header("Options")
save_to_db = st.sidebar.checkbox("Save report to local DB (enable carefully)", value=False)
if save_to_db:
    st.sidebar.info("Saving enabled locally. To persist automatically, set SAVE_RESULTS=true in backend env.")

st.sidebar.markdown("---")
if st.sidebar.button("View Analysis History"):
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM results ORDER BY id DESC LIMIT 200", conn)
        conn.close()
        st.subheader("📊 Recent saved reports")
        st.dataframe(df)
    else:
        st.info("No database file found (resume_results.db). Run an analysis and enable saving first.")

with st.form("upload_form"):
    uploaded = st.file_uploader("Upload your resume (PDF/DOCX/IMG)", type=["pdf","docx","png","jpg","jpeg"])
    jd_text = st.text_area("Paste Job Description (JD)", height=150)
    submitted = st.form_submit_button("Upload & Analyze")

if submitted and uploaded:
    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
    data = {"jd": jd_text or ""}
    with st.spinner("Analyzing your resume..."):
        resp = requests.post(API_URL, files=files, data=data)
    if resp.status_code == 200:
        out = resp.json()
        st.success(f"✅ Processed: {out['filename']}")

        st.subheader("📇 Contact Information")
        st.write(out["contact"])

        st.subheader("🧠 Skills Detected")
        st.write(out["skills"])

        st.subheader("🗂️ Resume Sections (Preview)")
        for k, v in out["sections"].items():
            st.markdown(f"**{k.title()}**")
            st.text(v[:800])

        if out.get("jd_match"):
            st.subheader("🎯 JD Match & ATS Score")
            jd = out["jd_match"]
            st.metric("Overall JD Fit Score", f"{jd['final_score']} / 100")
            st.write("**Breakdown:**")
            st.json(jd["breakdown"])

        if out.get("suggestions"):
            st.subheader("💡 Suggestions & Improvements")
            skills_sugg = out["suggestions"]["skill_suggestions"]
            st.markdown(
                "**Missing Skills:** "
                + (", ".join(skills_sugg["missing_skills"]) if skills_sugg["missing_skills"] else "No missing skills 🎯")
            )
            st.markdown("**Matched Skills:** " + ", ".join(skills_sugg["matched_skills"]))

            st.markdown("### 🧾 Resume Improvement Tips:")
            for tip in out["suggestions"]["text_suggestions"]:
                st.markdown(f"- {tip}")

        if out.get("ai_feedback"):
            st.subheader("🧠 Gemini Resume Coach Feedback")
            st.markdown(out["ai_feedback"])

        # LOCAL SAVE via backend env or manual toggle:
        if save_to_db:
            # Quick client-side save: POST to backend which may ignore save flag.
            # Prefer enabling SAVE_RESULTS in backend for automatic saves.
            st.info("Note: This client-side toggle does not change backend SAVE_RESULTS env. To persist server-side, set SAVE_RESULTS=true and restart backend.")
    else:
        st.error(f"❌ Server Error: {resp.status_code}")
