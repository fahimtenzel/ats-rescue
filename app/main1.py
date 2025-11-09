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
from app.gemini_feedback import generate_resume_feedback   # ✅ NEW IMPORT

# ---------------------------------------------------------
#  FASTAPI CONFIG
# ---------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
#  MAIN ROUTE
# ---------------------------------------------------------
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), jd: str = Form(None)):
    contents = await file.read()
    content_type = file.content_type or ""
    text = ""

    # Detect and extract text
    if "pdf" in content_type or file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(contents)
    elif file.filename.lower().endswith((".docx", ".doc")):
        text = extract_text_from_docx_bytes(contents)
    elif content_type.startswith("image/") or file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        text = extract_text_from_image_bytes(contents)
    else:
        text = extract_text_from_pdf_bytes(contents)

    # Basic parsing
    sections = split_into_sections(text)
    contact = extract_contact(text)
    skills = extract_skills(text)

    # ---------------------------------------------------------
    #  JD MATCHING + SUGGESTIONS + GEMINI FEEDBACK
    # ---------------------------------------------------------
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
        text_suggest = generate_text_suggestions(
            jd_match["final_score"], skill_suggest["missing_skills"]
        )

        suggestions = {
            "skill_suggestions": skill_suggest,
            "text_suggestions": text_suggest,
        }

        # Generate AI feedback via Gemini
        try:
            ai_feedback = generate_resume_feedback(jd, text, jd_match, suggestions)
        except Exception as e:
            ai_feedback = f"⚠️ Gemini feedback could not be generated: {e}"

    # ---------------------------------------------------------
    #  FINAL RESPONSE
    # ---------------------------------------------------------
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
