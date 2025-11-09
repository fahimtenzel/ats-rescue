# app/jd_match.py
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
import spacy

nlp = spacy.load("en_core_web_sm")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------------
#  BASIC TEXT PREPROCESSING
# -------------------------------------------------------
def preprocess(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------------------------------------
#  KEYWORD & SEMANTIC MATCHING
# -------------------------------------------------------
def keyword_overlap_score(jd_text: str, resume_text: str) -> float:
    vec = TfidfVectorizer(stop_words="english", max_features=2000)
    tfidf = vec.fit_transform([jd_text, resume_text])
    sim = (tfidf[0] @ tfidf[1].T).toarray()[0][0]  # ✅ fixed
    return float(sim)

def semantic_similarity_score(jd_text: str, resume_text: str) -> float:
    jd_emb = embed_model.encode(jd_text, convert_to_tensor=True)
    res_emb = embed_model.encode(resume_text, convert_to_tensor=True)
    sim = util.cos_sim(jd_emb, res_emb).item()
    return float(sim)

# -------------------------------------------------------
#  SKILL COVERAGE
# -------------------------------------------------------
def skill_coverage_score(jd_skills, resume_skills):
    jd_skills = [s.lower() for s in jd_skills]
    resume_skills = [s.lower() for s in resume_skills]
    if not jd_skills:
        return 0.0
    exact = len(set(jd_skills) & set(resume_skills))
    return exact / len(jd_skills)

# -------------------------------------------------------
#  EXPERIENCE RELEVANCE (very simple heuristic)
# -------------------------------------------------------
def experience_relevance_score(jd_text, resume_text):
    jd_doc = nlp(jd_text.lower())
    jd_nouns = [t.lemma_ for t in jd_doc if t.pos_ in ("NOUN", "PROPN")]
    matches = sum(1 for noun in jd_nouns if noun in resume_text.lower())
    return min(1.0, matches / max(10, len(jd_nouns)))

# -------------------------------------------------------
#  MAIN FUNCTION TO COMBINE ALL SCORES
# -------------------------------------------------------
def compute_jd_fit(jd_text, resume_text, jd_skills=None, resume_skills=None):
    jd_text = preprocess(jd_text)
    resume_text = preprocess(resume_text)
    jd_skills = jd_skills or []
    resume_skills = resume_skills or []

    kw = keyword_overlap_score(jd_text, resume_text)
    sem = semantic_similarity_score(jd_text, resume_text)
    skill_cov = skill_coverage_score(jd_skills, resume_skills)
    exp_rel = experience_relevance_score(jd_text, resume_text)

    # Weight combination (tweak later)
    w_kw, w_sem, w_skill, w_exp = 0.3, 0.3, 0.3, 0.1
    score = (w_kw * kw + w_sem * sem + w_skill * skill_cov + w_exp * exp_rel)
    final_score = round(score * 100, 1)

    return {
        "final_score": final_score,
        "breakdown": {
            "keyword_overlap": round(kw * 100, 1),
            "semantic_similarity": round(sem * 100, 1),
            "skill_coverage": round(skill_cov * 100, 1),
            "experience_relevance": round(exp_rel * 100, 1),
        },
    }
