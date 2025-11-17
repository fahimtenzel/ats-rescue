# app/gemini_feedback.py
import os
import google.generativeai as genai

# Set your Gemini API key (environment variable recommended)
genai.configure(api_key=os.getenv(API-KEY)

def generate_resume_feedback(jd_text: str, resume_text: str, jd_match: dict, suggestions: dict):
    """
    Generate AI-based feedback using Gemini, based on ATS analysis results.
    """
    prompt = f"""
    You are an expert ATS and career coach.
    Below are the extracted details:

    --- JOB DESCRIPTION ---
    {jd_text}

    --- RESUME TEXT ---
    {resume_text[:2000]}

    --- ATS SCORE BREAKDOWN ---
    {jd_match}

    --- MISSING SKILLS ---
    {', '.join(suggestions['skill_suggestions']['missing_skills'])}

    --- SUGGESTIONS ---
    {suggestions['text_suggestions']}

    Write a personalized feedback paragraph (150-200 words) that:
    - Sounds encouraging and professional.
    - Explains the resume’s strengths and weaknesses.
    - Suggests what the user can do to improve the JD match.
    - Avoids repeating the same skill list mechanically.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text
