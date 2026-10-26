"""Core resume-vs-job-description analysis logic."""
import re
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# A compact, multilingual-capable sentence embedding model. The first run downloads it.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None

# Starter skill dictionary; extend for your target roles and job market.
SKILL_TERMS = [
    "python", "java", "c++", "javascript", "typescript", "sql", "nosql",
    "machine learning", "deep learning", "natural language processing", "nlp",
    "generative ai", "llm", "langchain", "hugging face", "transformers",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "matplotlib",
    "data analysis", "data visualization", "statistics", "probability",
    "feature engineering", "model evaluation", "computer vision", "opencv",
    "spacy", "fastapi", "flask", "streamlit", "django", "rest api",
    "api development", "git", "github", "docker", "kubernetes", "linux",
    "aws", "azure", "gcp", "cloud computing", "postgresql", "mysql",
    "mongodb", "redis", "etl", "data engineering", "power bi", "tableau",
    "excel", "communication", "teamwork", "problem solving", "agile",
    "react", "node.js", "html", "css", "software testing", "unit testing",
    "data structures", "algorithms", "object oriented programming",
    "oop", "operating systems", "computer networks", "dbms"
]

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_skills(text: str) -> list[str]:
    """Match known skill phrases using boundaries to avoid many substring false positives."""
    lowered = text.lower()
    found = []
    for skill in SKILL_TERMS:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill.lower()) + r"(?![a-z0-9+#.])"
        if re.search(pattern, lowered):
            found.append(skill)
    return sorted(set(found))

def split_sections(resume: str) -> dict[str, str]:
    """Heuristic section detector; resume formats vary, so treat as guidance only."""
    labels = {
        "experience": ["experience", "work experience", "professional experience", "internship"],
        "projects": ["projects", "academic projects", "personal projects"],
        "education": ["education", "academic background", "qualifications"],
        "skills": ["skills", "technical skills", "core competencies"],
        "certifications": ["certifications", "certificates", "licenses"],
    }
    lines = [line.strip() for line in resume.splitlines() if line.strip()]
    result = {key: "" for key in labels}
    active = None
    for line in lines:
        normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
        matched = None
        for section, aliases in labels.items():
            if normalized in aliases:
                matched = section
                break
        if matched:
            active = matched
        elif active:
            result[active] += line + "\n"
    return {k: v.strip() for k, v in result.items()}

def analyze_resume(resume_text: str, job_description: str) -> dict[str, Any]:
    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)
    if len(resume_text) < 40:
        raise ValueError("The resume text is too short. Check that the PDF contains selectable text or upload a DOCX.")
    if len(job_description) < 40:
        raise ValueError("Please enter a more detailed job description (at least 40 characters).")

    model = _get_model()
    embeddings = model.encode(
        [resume_text, job_description],
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    similarity = float(np.dot(embeddings[0], embeddings[1]))
    # Cosine similarity can be negative; clamp for an interpretable percentage.
    semantic_score = round(max(0.0, min(1.0, similarity)) * 100, 1)

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)
    # If no known skills are found in the JD, avoid dividing by zero.
    skill_score = round(100 * len(matched) / len(job_skills), 1) if job_skills else 0.0

    # Transparent heuristic, not a real ATS vendor score.
    overall = round(0.65 * semantic_score + 0.35 * skill_score, 1)
    sections = split_sections(resume_text)
    recommendations = []
    if not sections["experience"]:
        recommendations.append("Add a clearly labelled Experience section if you have internships, work, volunteering, or relevant practical experience.")
    if not sections["projects"]:
        recommendations.append("Add 2–3 relevant projects. Explain the problem, your contribution, tools used, and measurable outcome.")
    if not sections["skills"]:
        recommendations.append("Add a clearly labelled Skills section containing skills you genuinely possess and can discuss in an interview.")
    if missing:
        recommendations.append("Review the missing-skill list. Add a skill only if you actually have that skill; otherwise consider learning it.")
    if len(resume_text.split()) < 250:
        recommendations.append("The extracted resume is quite short. Check whether content was missed during PDF extraction and consider adding relevant evidence.")
    if not recommendations:
        recommendations.append("Keep the resume tailored to this role and support important skills with concrete project or experience evidence.")

    strengths = []
    if matched:
        strengths.append("Your resume mentions these job-description skills: " + ", ".join(matched[:12]) + ("…" if len(matched) > 12 else "") + ".")
    if sections["projects"]:
        strengths.append("A Projects section appears to be present.")
    if sections["education"]:
        strengths.append("An Education section appears to be present.")
    if not strengths:
        strengths.append("The resume was compared semantically with the supplied job description; inspect the skill results and recommendations for specific next steps.")

    return {
        "overall_match_score": overall,
        "semantic_similarity_score": semantic_score,
        "skill_coverage_score": skill_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills_detected": sorted(resume_skills),
        "job_skills_detected": sorted(job_skills),
        "strengths": strengths,
        "recommendations": recommendations,
        "section_presence": {k: bool(v.strip()) for k, v in sections.items()},
        "disclaimer": "This is an educational heuristic, not an official ATS score, hiring decision, or guarantee of shortlisting. Skill extraction uses a limited dictionary and can miss synonyms or context."
    }
