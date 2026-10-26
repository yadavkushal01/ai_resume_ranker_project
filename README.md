# TalentMind AI Resume Optimizer & ATS Matcher

TalentMind AI Resume Optimizer & ATS Matcher is an AI-powered resume analysis platform that helps students tailor their resumes to a target job description and helps recruiters compare multiple applicants. It combines semantic similarity, skill coverage, resume section checks, and improvement recommendations in one interface.

The application supports two workflows:

- **Individual Resume Analysis:** Upload one resume to receive a match score, semantic similarity, skill coverage, matched skills, missing skills, strengths, and improvement suggestions. A single resume is not ranked against other candidates.
- **Multi-Resume Candidate Ranking:** Upload multiple resumes against the same job description to compare candidates and sort them by the project's match score. Select a candidate to inspect their detailed analysis.
- **Resume Improvement:** Request an improved resume draft based on the target job description and the original resume. Review the output carefully before using it.

> **Important:** Match scores are project-defined estimates, not official ATS scores, hiring decisions, or guarantees of shortlisting. Rankings should be treated as decision support and reviewed by a human.

## Features

### Resume analysis
- Upload PDF and DOCX resumes.
- Extract text from uploaded resumes.
- Compare resume content and job descriptions using sentence-transformer embeddings.
- Calculate a transparent weighted match score using semantic similarity and skill coverage.
- Detect skills using a starter skill dictionary.
- Display matched skills, missing skills, detected resume skills, and job skills.
- Provide strengths, resume-section presence checks, and actionable suggestions.
- Support a single-resume workflow without candidate ranking.

### Multi-resume comparison
- Upload multiple resumes for the same job description.
- Analyze each resume and sort candidates by the project's match score.
- Show candidate cards with available name, rank, score, and summary information.
- Open a detailed candidate view for individual analysis.
- Handle resumes where a name or other profile details cannot be extracted; the filename can be used as a fallback label.

### Resume improvement
- Generate a draft using the available improvement workflow.
- Use the job description and original resume as context for suggestions.
- Review and edit the draft before downloading or sharing it.
- The current starter implementation may provide a structured draft/checklist rather than fully rewritten, LLM-generated bullet points. A generative model integration is required for advanced automatic rewriting.

### User interface
- React, TypeScript, and Vite frontend.
- Responsive recruiter/student dashboard.
- Drag-and-drop file upload with file validation.
- Job description editor with character count and validation.
- Loading and processing states, error feedback, and results views.
- Backend URL configured through `VITE_API_URL`.

### Backend
- FastAPI REST API.
- PDF and DOCX text extraction.
- Sentence Transformers semantic embeddings.
- Scikit-learn cosine similarity.
- Skill coverage and heuristic section detection.
- API documentation through FastAPI Swagger UI.

## Tech Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- TanStack Router / project routing setup
- Sonner or the configured toast library

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Sentence Transformers
- Hugging Face model: `sentence-transformers/all-MiniLM-L6-v2`
- Scikit-learn
- NumPy
- pypdf
- python-docx
- python-multipart

## Project Architecture

- `frontend/` contains the React application, components, route definitions, API service layer, types, styling, and static assets.
- `backend/` contains the FastAPI application and resume analysis logic.
- The frontend sends resumes and the job description to the backend as multipart form data.
- The backend extracts resume text, runs NLP analysis, and returns structured JSON results.
- Batch analysis applies the same analysis pipeline to each resume and sorts results for comparison.

## Folder Structure

```text
TalentMind_Resume_Optimizer/
├── backend/
│   ├── myenv/
│   ├── api.py
│   ├── analyzer.py
│   └── requirements.txt
├── frontend/
│   ├── node_modules/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── routes.tsx
│   │   ├── reuteTree.gen.ts
│   │   ├── server.ts
│   │   ├── start.ts
│   │   └── style.css
│   ├── .env
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

> The exact file list can differ slightly between project ZIP versions. Keep this structure section aligned with the files in the version you submit.

## Requirements

### Python
- Python 3.11 or newer recommended.
- `pip` available.
- Internet access on the first run to download the Hugging Face model.
- Enough disk space for Python dependencies and the model cache.

### Node.js
- Node.js 22 or newer recommended.
- `npm` available.

## Installation

### 1. Backend installation

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, you can activate it from Command Prompt with:

```bat
.venv\Scripts\activate.bat
```

### 2. Frontend installation

Open a second terminal from the project root:

```powershell
cd frontend
npm install
```

## Environment Variables

Create or edit `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Restart the Vite development server after changing environment variables.

## Running the Application

### Run the backend

From the project root:

```powershell
cd backend
.venv\Scripts\activate
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

If your backend entry file is named `main.py` rather than `api.py`, use `uvicorn main:app --reload --host 127.0.0.1 --port 8000`. The command must match the Python filename that defines `app = FastAPI(...)`.

The backend should be available at:

- API root: `http://127.0.0.1:8000/`
- Interactive API docs: `http://127.0.0.1:8000/docs`
- Health check, if implemented: `http://127.0.0.1:8000/health`

### Run the frontend

In a separate terminal:

```powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

Keep both backend and frontend terminals running while using the application.

## API Overview

The exact request and response schemas depend on the backend version included in your project. The intended API surface is described below; check `http://127.0.0.1:8000/docs` for the authoritative schemas.

### Health / root

```http
GET /
```

Example response:

```json
{
  "message": "TalentMind AI Resume Optimizer backend is running."
}
```

### Analyze one resume

```http
POST /analyze
Content-Type: multipart/form-data
```

Expected form fields:

- `resume`: one PDF or DOCX file
- `job_description`: target job description text

The response includes the resume filename, overall match score, semantic similarity score, skill coverage score, matched skills, missing skills, detected skills, strengths, recommendations, and section-presence checks, depending on the deployed backend version.

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "resume=@resume.pdf" \
  -F "job_description=We are looking for a Python developer with SQL, machine learning, and API development experience."
```

### Analyze multiple resumes

```http
POST /analyze-batch
Content-Type: multipart/form-data
```

Intended form fields:

- `job_description`: one shared job description
- Multiple `files` fields containing PDF/DOCX resumes, according to the endpoint's implementation

The response should include a summary and a list of analyzed candidates sorted by match score. A single uploaded resume should use the individual-analysis view rather than a ranked comparison.

> Multipart field names must exactly match the backend implementation. Confirm the batch endpoint's parameter names in `/docs` and ensure the frontend API service uses the same names.

### Generate an improved resume draft

```http
POST /improve-resume
Content-Type: multipart/form-data
```

Intended inputs:

- The original resume or extracted resume text
- The target job description
- Any additional fields required by the endpoint

The response should contain the improved draft or a structured set of suggestions. Check `/docs` for the exact request fields and response schema.

## How Matching Works

The starter analyzer uses two components:

1. **Semantic similarity:** A sentence-transformer model encodes the resume and job description into vectors. Cosine similarity estimates how closely their content aligns.
2. **Skill coverage:** A starter dictionary detects known skill terms in the job description and resume. Coverage is the proportion of detected job-description skills also found in the resume.

The baseline scoring formula is:

```text
overall_match_score = 0.65 * semantic_similarity_score
                    + 0.35 * skill_coverage_score
```

Scores are scaled to 0–100. Multi-resume results can be sorted by this score.

This is a transparent heuristic for a student project, not a validated hiring model. Dictionary-based extraction may miss synonyms, context, transferable skills, and skills expressed in different ways. Similarity is not the same as qualification.

## Resume Improvement Workflow

The improvement feature is designed to help users tailor an existing resume to a role. A production-ready implementation should:

- Preserve the candidate's actual work history, education, projects, and skills.
- Rewrite for clarity and relevance without inventing qualifications, employers, dates, metrics, or certifications.
- Highlight suggested changes and allow the user to edit the result.
- Offer a DOCX download and, optionally, a PDF export.
- Clearly label generated text for review before use.

If the current code only generates a structured draft or checklist, connect a suitable LLM provider to implement full automatic rewriting. Keep API keys in backend environment variables and never expose secrets through `VITE_` frontend variables.

## Supported Resume Formats and Limitations

- PDF files with selectable text and DOCX documents are supported by the starter parser.
- Scanned/image-only PDFs may return little or no text. OCR is needed to support those files.
- Candidate names and contact information are extracted only if the parser or analysis code implements that extraction. A filename fallback should be used when details are unavailable.
- Complex tables, columns, graphics, headers, and footers can affect extraction quality.
- The initial skill dictionary is editable in the backend code.

## Privacy, Security, and Responsible Use

- Treat resumes as sensitive personal information.
- Do not upload resumes without appropriate permission.
- Avoid logging complete resume contents or personal contact information.
- Before public deployment, add authentication, file-size and rate limits, HTTPS, appropriate CORS restrictions, deletion/retention controls, and secure error handling.
- Do not use automated match scores as the sole basis for hiring or rejecting candidates. Human review is required.
- Give candidates an opportunity to correct parsing errors and review generated resume edits.
- Do not invent or exaggerate qualifications when generating an improved resume.

## Future Scope

- Integrate an LLM for complete resume rewriting and personalized feedback.
- Generate downloadable DOCX/PDF resumes.
- Add OCR for scanned resumes.
- Improve skill extraction with spaCy, taxonomy matching, and synonym support.
- Add filters, sorting, and side-by-side candidate comparison.
- Export candidate analysis to CSV/Excel/PDF.
- Add recruiter accounts, saved job descriptions, and analysis history.
- Add model evaluation, fairness checks, and transparent scoring controls.
- Deploy the frontend and backend with appropriate security and privacy protections.

## Troubleshooting

### Frontend cannot connect to backend
- Confirm the backend is running on port `8000`.
- Check `VITE_API_URL` in `frontend/.env`.
- Confirm the frontend request path and multipart field names match the backend.
- Restart Vite after editing `.env`.

### Model downloads slowly
- The first analysis downloads the sentence-transformer model.
- Keep internet access available for the initial download.
- Check the backend terminal for the specific error.

### No text is extracted from a PDF
- Try a PDF with selectable text or a DOCX file.
- Scanned PDFs require OCR support.

### Batch analysis fails
- Check the batch endpoint and exact multipart field names in `/docs`.
- Ensure each uploaded file is PDF or DOCX and within the configured size limit.
- Review backend logs for the underlying error.

## License

Choose and add the license that matches your intended use and any third-party dependencies.

## Project Summary

**TalentMind AI Resume Optimizer & ATS Matcher** combines semantic NLP, skill-gap analysis, multi-resume comparison, and resume-improvement workflows in a responsive full-stack application for students and recruiters.
