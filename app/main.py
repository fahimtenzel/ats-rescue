# app/main.py
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

from app.extract import (
    extract_text_from_pdf_bytes,
    extract_text_from_docx_bytes,
    extract_text_from_image_bytes,
)
from app.parse import split_into_sections, extract_contact, extract_skills
from app.jd_match import compute_jd_fit
from app.suggestions import generate_skill_suggestions, generate_text_suggestions
from app.gemini_feedback import generate_resume_feedback

# DB helpers
from app.db import init_db, save_result  # new

# ---------------------------------------------------------
#  FASTAPI CONFIG
# ---------------------------------------------------------
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize DB schema if saving is enabled (but safe to call always)
try:
    init_db()
except Exception as e:
    # don't block app if DB init fails; log to console
    print("Warning: init_db failed:", e)

# Read environment flag (default off)
SAVE_RESULTS = os.getenv("SAVE_RESULTS", "false").lower() in ("1", "true", "yes")

# ---------------------------------------------------------
#  MAIN ROUTE
# ---------------------------------------------------------
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), jd: str = Form(None)):
    contents = await file.read()
    content_type = file.content_type or ""
    text = ""

    # Extract text by file type
    if "pdf" in content_type or file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(contents)
    elif file.filename.lower().endswith((".docx", ".doc")):
        text = extract_text_from_docx_bytes(contents)
    elif content_type.startswith("image/") or file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        text = extract_text_from_image_bytes(contents)
    else:
        text = extract_text_from_pdf_bytes(contents)

    # Parse
    sections = split_into_sections(text)
    contact = extract_contact(text)
    skills = extract_skills(text)

    # JD Matching & suggestions
    jd_match = None
    suggestions = None
    ai_feedback = None

    if jd and len(jd.strip()) > 0:
        jd_match = compute_jd_fit(jd, text, resume_skills=skills)

        jd_keywords = [
            "python", "sql", "excel", "pandas", "power bi", "tableau",
            "communication", "analytics", "data visualization", "machine learning"
        ]

        skill_suggest = generate_skill_suggestions(jd_keywords, skills)
        text_suggest = generate_text_suggestions(jd_match["final_score"], skill_suggest["missing_skills"])

        suggestions = {
            "skill_suggestions": skill_suggest,
            "text_suggestions": text_suggest,
        }

        # Gemini feedback (may raise if key missing; handled below)
        try:
            ai_feedback = generate_resume_feedback(jd, text, jd_match, suggestions)
        except Exception as e:
            ai_feedback = f"⚠️ Gemini feedback could not be generated: {e}"

        # --- CONDITIONAL SAVE: only if SAVE_RESULTS is true ---
        if SAVE_RESULTS:
            try:
                missing = suggestions["skill_suggestions"].get("missing_skills", [])
                matched = suggestions["skill_suggestions"].get("matched_skills", [])
                save_result(
                    filename=file.filename,
                    jd_text=jd,
                    ats_score=jd_match.get("final_score", 0),
                    breakdown=jd_match.get("breakdown", {}),
                    missing_skills=missing,
                    matched_skills=matched,
                    ai_feedback=ai_feedback or ""
                )
            except Exception as e:
                # Do not fail the API if DB save fails; log and continue
                print("Warning: failed to save result to DB:", e)

    # Final response
    return {
        "filename": file.filename,
        "text_snippet": text[:2000],
        "sections": sections,
        "contact": contact,
        "skills": skills,
        "jd_match": jd_match,
        "suggestions": suggestions,
        "ai_feedback": ai_feedback,
    }
