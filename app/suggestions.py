# app/suggestions.py
from typing import List

def generate_skill_suggestions(jd_skills: List[str], resume_skills: List[str]):
    """Find missing and matched skills."""
    jd_lower = [s.lower() for s in jd_skills]
    res_lower = [s.lower() for s in resume_skills]
    missing = [s for s in jd_lower if s not in res_lower]
    matched = [s for s in jd_lower if s in res_lower]
    return {
        "missing_skills": missing,
        "matched_skills": matched,
    }

def generate_text_suggestions(score: float, missing_skills: List[str]):
    """Basic rule-based text suggestions before Gemini feedback."""
    tips = []

    if score < 50:
        tips.append(
            "Your resume and JD match is quite low. Focus on adding more relevant skills and improving the experience section."
        )
    elif 50 <= score < 75:
        tips.append(
            "Decent match! Add more role-specific keywords and quantify your achievements."
        )
    else:
        tips.append(
            "Strong match! Just polish your language and format for clarity."
        )

    if missing_skills:
        tips.append(
            f"Consider adding these skills or mentioning relevant experience: {', '.join(missing_skills[:5])}."
        )
    else:
        tips.append("All major JD skills are already covered — great job!")

    tips.append("Ensure your resume is saved as a text-based PDF (not scanned).")

    return tips
