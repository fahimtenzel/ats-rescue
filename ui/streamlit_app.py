# ui/streamlit_app.py
import streamlit as st
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:8000/upload"
DB_PATH = Path("resume_results.db")

# --- Page config and minimal styling ---
st.set_page_config(page_title="Fluentorr ATS Coach", layout="wide")

# small CSS for modern feel
st.markdown(
    """
    <style>
    .reportview-container { font-family: 'Inter', Roboto, sans-serif; }
    .stApp { background-color: #fafafa; }
    .card {
        background: white; padding: 18px; border-radius: 12px;
        box-shadow: 0 4px 18px rgba(17,24,39,0.06);
        margin-bottom: 18px;
    }
    .muted { color: #6b7280; }
    .big-score { font-size: 48px; font-weight:700; margin: 6px 0; }
    .small { font-size: 13px; color:#6b7280; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📄 Fluentorr — ATS Resume Coach")
    st.markdown("Upload your resume and paste the role's Job Description (JD). You'll get an ATS score, targeted suggestions, and a short AI-generated coach note.")
with col2:
    st.write("")  # keep alignment
    if DB_PATH.exists():
        st.success("History available")
    else:
        st.info("No saved history yet")

st.markdown("---")

# --- Sidebar options ---
st.sidebar.header("Options")
save_to_db = st.sidebar.checkbox("Save report to local DB (opt-in)", value=False)
st.sidebar.markdown("**Quick actions**")
if st.sidebar.button("View Analysis History"):
    if DB_PATH.exists():
        import sqlite3, pandas as pd
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, timestamp, filename, ats_score FROM results ORDER BY id DESC LIMIT 200", conn)
        conn.close()
        st.subheader("📊 Recent saved reports")
        st.dataframe(df)
    else:
        st.info("No history found. Enable save & run an analysis.")

# --- Upload form ---
with st.form("upload_form", clear_on_submit=False):
    uploaded = st.file_uploader("Upload your resume (PDF/DOCX/IMG)", type=["pdf","docx","png","jpg","jpeg"])
    jd_text = st.text_area("Paste Job Description (JD) — the role you want to target", height=160)
    submitted = st.form_submit_button("Upload & Analyze")

# --- Main panel: show summary first, then details ---
if submitted and uploaded:
    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
    data = {"jd": jd_text or ""}
    with st.spinner("Analyzing your resume..."):
        resp = requests.post(API_URL, files=files, data=data)

    if resp.status_code != 200:
        st.error(f"Server error: {resp.status_code}")
    else:
        out = resp.json()

        # Top summary card with scores and suggestions
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            top_col1, top_col2 = st.columns([2, 3])

            # Left: Scores
            with top_col1:
                st.markdown("**🎯 Overall ATS Fit**")
                if out.get("jd_match"):
                    overall = out["jd_match"]["final_score"]
                    st.markdown(f"<div class='big-score'>{overall} / 100</div>", unsafe_allow_html=True)
                    # small visual progress bar
                    st.progress(int(min(max(overall, 0), 100)))
                    st.markdown("<div class='small muted'>Overall fit: weighted combination of keywords, semantic fit, skills, experience.</div>", unsafe_allow_html=True)
                    # show JD semantic quickly if present
                    breakdown = out["jd_match"].get("breakdown", {})
                    sem = breakdown.get("semantic_similarity", None)
                    kw = breakdown.get("keyword_overlap", None)
                    if sem is not None or kw is not None:
                        st.write("")
                        c1, c2 = st.columns(2)
                        if kw is not None:
                            c1.metric("Keyword overlap", f"{kw} / 100")
                        if sem is not None:
                            c2.metric("Semantic similarity", f"{sem} / 100")
                else:
                    st.markdown("<div class='big-score'>—</div>", unsafe_allow_html=True)
                    st.info("No JD provided — paste a Job Description to get a fit score.")

            # Right: Suggestions summary
            with top_col2:
                st.markdown("**💡 Top Suggestions (quick view)**")
                if out.get("suggestions"):
                    sugg = out["suggestions"]
                    skills_sugg = sugg.get("skill_suggestions", {})
                    missing = skills_sugg.get("missing_skills", [])
                    matched = skills_sugg.get("matched_skills", [])

                    # concise chips
                    if missing:
                        st.markdown("**Missing skills:**")
                        st.markdown(", ".join([f"`{s}`" for s in missing[:8]]))
                    else:
                        st.success("All major JD skills covered 🎯")

                    st.markdown("**Matched skills:**")
                    st.markdown(", ".join([f"`{s}`" for s in matched[:8]]))

                    # Expand for tips
                    with st.expander("View improvement tips"):
                        for tip in sugg.get("text_suggestions", []):
                            st.markdown(f"- {tip}")
                else:
                    st.info("No suggestions available. Provide a JD to get tailored suggestions.")

            st.markdown("</div>", unsafe_allow_html=True)

        # AI Feedback card (Gemini)
        if out.get("ai_feedback"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("🧠 AI Resume Summary")
            st.markdown(out["ai_feedback"])
            st.markdown("</div>", unsafe_allow_html=True)

        # Option: show parsed details (hidden by default, for debugging)
        with st.expander("🔎 Internal parsed outputs (hidden) — show only for debugging"):
            st.subheader("Contact")
            st.json(out.get("contact", {}))
            st.subheader("Detected Skills")
            st.json(out.get("skills", []))
            st.subheader("Raw JD match breakdown")
            st.json(out.get("jd_match", {}))
            st.subheader("Full suggestions object")
            st.json(out.get("suggestions", {}))

        # Bottom CTA: export or copy suggestions
        with st.container():
            c1, c2, c3 = st.columns([1,1,2])
            if c1.button("Copy suggestions"):
                # copy to clipboard not directly supported; provide text area to copy
                suggestions_text = ""
                if out.get("suggestions"):
                    skills_sugg = out["suggestions"]["skill_suggestions"]
                    missing = skills_sugg.get("missing_skills", [])
                    matched = skills_sugg.get("matched_skills", [])
                    suggestions_text += "Missing skills: " + ", ".join(missing) + "\n"
                    suggestions_text += "Matched skills: " + ", ".join(matched) + "\n\n"
                    for tip in out["suggestions"]["text_suggestions"]:
                        suggestions_text += "- " + tip + "\n"
                st.text_area("Copy suggestions below", suggestions_text, height=160)
            if c2.button("Export as TXT"):
                # create a blob-like download via st.download_button
                export_text = ""
                if out.get("suggestions"):
                    skills_sugg = out["suggestions"]["skill_suggestions"]
                    export_text += "Missing skills: " + ", ".join(skills_sugg.get("missing_skills", [])) + "\n"
                    export_text += "Matched skills: " + ", ".join(skills_sugg.get("matched_skills", [])) + "\n\n"
                    for tip in out["suggestions"]["text_suggestions"]:
                        export_text += "- " + tip + "\n"
                st.download_button("Download suggestions (.txt)", export_text, file_name="suggestions.txt")
            # Save note
            if save_to_db:
                c3.info("Save enabled locally. To persist server-side automatically, set SAVE_RESULTS=true in backend env and restart the backend.")
