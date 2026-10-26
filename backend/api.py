"""FastAPI service for resume analysis."""
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from analyzer import analyze_resume, clean_text

app = FastAPI(
    title="AI Resume Optimizer & ATS Matcher",
    description="Semantic resume matching and skill-gap analysis.",
    version="1.0.0",
)

# Development CORS for the local Vite frontend. Restrict origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_BYTES = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def extract_resume_text(filename: str, raw: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Upload a PDF or DOCX file.")
    if ext == ".pdf":
        reader = PdfReader(BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    document = Document(BytesIO(raw))
    paragraphs = [p.text for p in document.paragraphs]
    # Include text in simple tables, where resumes often place content.
    for table in document.tables:
        for row in table.rows:
            paragraphs.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(paragraphs)

@app.get("/")
def root():
    return {"message": "Resume Optimizer API is running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(
    job_description: str = Form(...),
    resume: UploadFile = File(...),
):
    raw = await resume.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 8 MB.")
    try:
        resume_text = extract_resume_text(resume.filename or "", raw)
        result = analyze_resume(resume_text, job_description)
        return {
            "filename": resume.filename,
            "extracted_text_preview": resume_text[:1200],
            **result
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Avoid returning internal stack traces or local paths to the client.
        raise HTTPException(status_code=500, detail="Analysis failed. Check the API terminal for the error.") from exc


import re
from datetime import datetime, timezone
from typing import List

MAX_BATCH_FILES = 20

def extract_identity(text: str, filename: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # A conservative heuristic: use the first plausible short line, otherwise filename.
    name = next((line for line in lines[:8] if len(line) <= 70 and not re.search(r'@|https?://|\d{5,}|resume|curriculum vitae', line, re.I)), Path(filename).stem.replace('_', ' ').replace('-', ' ').title())
    email_match = re.search(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', text, re.I)
    phone_match = re.search(r'(?<!\w)(?:\+?\d[\d ()-]{8,}\d)(?!\w)', text)
    experience_match = re.search(r'(\d{1,2})\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience', text, re.I)
    return {
        'candidate_name': name[:90],
        'email': email_match.group(0) if email_match else None,
        'phone': phone_match.group(0).strip() if phone_match else None,
        'experience_years_mentioned': int(experience_match.group(1)) if experience_match else None,
    }

async def read_resume_file(upload: UploadFile) -> tuple[str, str]:
    raw = await upload.read()
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError(f'{upload.filename}: file exceeds the 8 MB limit.')
    filename = upload.filename or 'resume'
    text = extract_resume_text(filename, raw)
    if len(text.strip()) < 40:
        raise ValueError(f'{filename}: too little text could be extracted. For scanned PDFs, OCR is needed.')
    return filename, clean_text(text)

@app.post('/analyze-batch')
async def analyze_batch(job_description: str = Form(...), resumes: List[UploadFile] = File(...)):
    if len(job_description.strip()) < 40:
        raise HTTPException(status_code=400, detail='Please provide a job description with at least 40 characters.')
    if not resumes:
        raise HTTPException(status_code=400, detail='Upload at least one resume.')
    if len(resumes) > MAX_BATCH_FILES:
        raise HTTPException(status_code=400, detail=f'Upload up to {MAX_BATCH_FILES} resumes per batch.')
    candidates = []
    errors = []
    for upload in resumes:
        try:
            filename, text = await read_resume_file(upload)
            result = analyze_resume(text, job_description)
            identity = extract_identity(text, filename)
            candidates.append({
                **identity,
                'filename': filename,
                'extracted_text_preview': text[:1800],
                'resume_word_count': len(text.split()),
                **result,
            })
        except ValueError as exc:
            errors.append(str(exc))
        except Exception:
            errors.append(f'{upload.filename or "Resume"}: analysis failed. Check backend terminal.')
    if not candidates:
        raise HTTPException(status_code=400, detail='No resumes could be analyzed. ' + ' '.join(errors))
    candidates.sort(key=lambda item: item['overall_match_score'], reverse=True)
    for rank, candidate in enumerate(candidates, start=1):
        candidate['rank'] = rank if len(candidates) > 1 else None
    return {
        'job_description': job_description,
        'mode': 'ranking' if len(candidates) > 1 else 'single',
        'summary': {
            'total_uploaded': len(resumes),
            'total_analyzed': len(candidates),
            'failed_count': len(errors),
            'analyzed_at': datetime.now(timezone.utc).isoformat(),
        },
        'candidates': candidates,
        'errors': errors,
    }

@app.post('/improve-resume')
async def improve_resume(job_description: str = Form(...), resume: UploadFile = File(...)):
    """Create an honest, editable resume draft using existing resume content and job context."""
    try:
        filename, text = await read_resume_file(resume)
        result = analyze_resume(text, job_description)
        # A safe starter draft: preserves the source content and adds tailored guidance, without inventing achievements.
        improved = (
            f"RESUME OPTIMIZATION DRAFT\nSource file: {filename}\n\n"
            "IMPORTANT: Review and edit this draft before using it. Do not keep any statement that is not true.\n\n"
            "PROFILE / SUMMARY\n"
            "Write a 2–4 line summary that connects your real experience to the target role. Mention only skills supported by the original resume.\n\n"
            "TARGET ROLE JOB DESCRIPTION\n" + job_description.strip() + "\n\n"
            "EXISTING RESUME CONTENT (preserved for editing)\n" + text + "\n\n"
            "TAILORING CHECKLIST\n" + "\n".join(f"- {item}" for item in result['recommendations']) + "\n\n"
            "SKILLS TO VERIFY BEFORE ADDING\n" + (', '.join(result['missing_skills']) if result['missing_skills'] else 'No missing skills detected by the starter skill dictionary.') + "\n"
            "Only add a missing skill if you genuinely possess it and can support it with evidence. Add measurable outcomes only when you can verify the numbers.\n"
        )
        return {'filename': filename, 'suggested_filename': Path(filename).stem + '_improvement_draft.txt', 'improved_resume_text': improved, 'analysis': result, 'notice': 'This is an editable first draft and checklist, not an automatically rewritten or verified resume. Review every statement for accuracy.'}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail='Resume improvement failed. Check the backend terminal.') from exc
