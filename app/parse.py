# app/parse.py
import re
import spacy
nlp = spacy.load("en_core_web_sm")

SECTION_HEADERS = [
    "experience","work experience","professional experience",
    "education","skills","projects","certifications","summary","objective",
    "contact","publications","achievements"
]

def split_into_sections(text: str) -> dict:
    text = text.replace("\r", "\n")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # naive header detection
    sections = {}
    current = "header"
    sections[current] = []
    for line in lines:
        low = line.lower()
        matched = None
        for h in SECTION_HEADERS:
            if low.startswith(h):
                matched = h
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
            # if header line contains more than header text, skip storing header itself
            continue
        sections.setdefault(current, []).append(line)
    # convert lists to text
    return {k: "\n".join(v) for k, v in sections.items()}

def extract_contact(text: str) -> dict:
    # simple email/phone extraction
    email = None
    phone = None
    m = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if m:
        email = m.group(0)
    m2 = re.search(r'(\+?\d[\d\-\s]{7,}\d)', text)
    if m2:
        phone = m2.group(0)
    return {"email": email, "phone": phone}

def extract_skills(text: str, skills_db: list = None) -> list:
    # very basic: look for comma/bullet separated tokens in 'skills' section or fallback to keyword match
    skills_db = skills_db or ["python","sql","excel","aws","docker","git","tensorflow","pandas","nlp","java","c++","spark"]
    text_low = text.lower()
    found = []
    for s in skills_db:
        if s.lower() in text_low:
            found.append(s)
    return found
