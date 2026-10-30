# Resume Parsing API
### Infosys Springboard Virtual Internship Program 7.0 — Assignment 2

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791.svg)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-fitz-orange.svg)](https://pymupdf.readthedocs.io/)
[![python-docx](https://img.shields.io/badge/python--docx-1.1+-blue.svg)](https://python-docx.readthedocs.io/)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen.svg)]()

---

## 1. Project Overview & Objective

The **Resume Parsing API** is a high-performance, production-grade REST API built using **FastAPI** and **PostgreSQL**. It is created as **Assignment 2** for the **Infosys Springboard Virtual Internship Program 7.0**.

The core objective of this application is to accept candidate resumes in **PDF** or **DOCX** formats, extract textual content safely, apply modular rule-based information extraction using Python and regular expressions, convert candidate details into validated structured JSON, and persist both the physical document and extracted structured records in a PostgreSQL relational database.

> **Note on Scope**: Per assignment specifications, this project is completely independent from Assignment 1. It does not implement user registration, login, logout, password reset, or JWT authentication.

---

## 2. Key Features

- **Multi-Format Ingestion**: Supports `.pdf` (via PyMuPDF) and `.docx` (via python-docx) file uploads.
- **Robust Upload Validation**:
  - File extension checking (`.pdf`, `.docx`).
  - Magic byte / file header signature verification (rejects renamed/spoofed files).
  - Configurable maximum upload file size (default: 5 MB).
  - Empty file detection (HTTP 400).
  - Collision-resistant UUID-based server-side storage naming (prevents path traversal).
- **Comprehensive Rule-Based Extraction**:
  - Full Name (top lines heuristic, ignoring emails, phone numbers, and section headers).
  - Email Address (RFC-compliant regex).
  - Phone Number (Indian mobile formats `+91`, 10-digit mobile, and international formats).
  - Address / Location (labeled addresses and Indian/international city detection).
  - Social Profiles (LinkedIn and GitHub profile URLs normalized).
  - Professional Summary / Career Objective.
  - Categorized Skills: All Skills, Technical Skills (languages, frameworks, DBs, cloud/DevOps), and Soft Skills.
  - Education (degrees: B.Tech, M.Tech, B.Sc, BCA, MCA, MBA, institutions, years, CGPA/GPA).
  - Work Experience & Internships (differentiated, company/org, role, tenure, descriptions).
  - Projects (title, description, and technologies identified).
  - Certifications (AWS, Infosys, Coursera, Oracle, etc. with issue years).
  - Spoken Languages (English, Hindi, Telugu, Tamil, and international languages).
  - Achievements / Awards.
  - Other Relevant Information (extracurricular, volunteer, hobbies).
  - Zero fabrication: returns `null` for missing scalar fields and `[]` for missing list fields.
- **PostgreSQL Persistence**:
  - SQLAlchemy 2.0 ORM with PostgreSQL JSONB storage for structured data.
  - Clean database session lifecycle with connection pooling and health checks.
  - Safe transactional rollback and disk file cleanup on database errors.
- **Database Migrations**: Managed using Alembic.
- **RESTful Endpoints & Swagger UI**: Full interactive OpenAPI documentation at `/docs`.
- **Automated Testing Suite**: 23 pytest tests with TestClient and programmatic fixtures (zero external files required to run tests).

---

## 3. Technology Stack

| Component | Technology | Version / Specification |
|---|---|---|
| **Programming Language** | Python | 3.11 or later (tested on 3.14.2) |
| **Web Framework** | FastAPI | >= 0.115.0 |
| **ASGI Server** | Uvicorn | >= 0.30.0 |
| **Database** | PostgreSQL | 14+ |
| **Database Driver** | Psycopg 3 | >= 3.1.18 (`psycopg[binary]`) |
| **ORM** | SQLAlchemy | 2.0+ |
| **Migrations** | Alembic | >= 1.13.0 |
| **Validation & Schemas** | Pydantic | 2.0+ (`pydantic-settings`) |
| **PDF Extraction** | PyMuPDF (`pymupdf`) | >= 1.24.0 |
| **DOCX Extraction** | python-docx | >= 1.1.0 |
| **Testing** | pytest & HTTPX | >= 8.2.0 |
| **API Docs** | Swagger UI & OpenAPI | Built-in |

---

## 4. Project Structure

```
resume-parsing-api/
│
├── app/
│   ├── __init__.py               # Application package definition
│   ├── main.py                   # FastAPI app, lifespan, and exception handlers
│   ├── config.py                 # Pydantic Settings configuration loader
│   ├── database.py               # SQLAlchemy 2.x engine, session, and health check
│   ├── models.py                 # SQLAlchemy Resume database model
│   ├── schemas.py                # Pydantic 2 request and response schemas
│   ├── exceptions.py             # Custom application exception hierarchy
│   │
│   ├── routers/
│   │   ├── __init__.py           # Routers package
│   │   └── resume.py             # REST endpoints (/api/v1/resumes and /health)
│   │
│   ├── services/
│   │   ├── __init__.py           # Services package
│   │   ├── file_service.py       # File validation, storage, and dispatch
│   │   ├── pdf_service.py        # PyMuPDF text extraction
│   │   ├── docx_service.py       # python-docx paragraphs and tables extraction
│   │   ├── extraction_service.py # Rule-based regex information extractor
│   │   └── resume_service.py     # Resume CRUD orchestration & persistence
│   │
│   └── utils/
│       ├── __init__.py           # Utils package
│       ├── validators.py         # File extension, size, and magic bytes validation
│       └── file_utils.py         # UUID naming and safe filesystem operations
│
├── migrations/
│   ├── env.py                    # Alembic migration runner
│   ├── script.py.mako            # Migration template
│   └── versions/
│       └── 001_initial_create_resumes_table.py  # Initial resumes table migration
│
├── tests/
│   ├── __init__.py               # Tests package
│   ├── conftest.py               # Pytest fixtures and test database isolation
│   ├── test_resume_upload.py     # Upload, format, validation, and health tests
│   ├── test_resume_extraction.py # Regex extraction unit tests
│   └── test_resume_database.py   # DB persistence, retrieval, pagination, deletion
│
├── uploads/
│   └── .gitkeep                  # Upload directory tracking (files git-ignored)
│
├── sample_resumes/
│   ├── README.md                 # Sample resumes guide
│   ├── sample_resume.pdf         # Generated sample resume (PDF)
│   └── sample_resume.docx        # Generated sample resume (DOCX)
│
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git exclusions
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Production and test dependencies
└── README.md                     # Comprehensive documentation
```

---

## 5. Prerequisites

Before setting up the project, ensure you have:
1. **Python 3.11+** installed (check using `python --version`).
2. **PostgreSQL** installed and running locally (or accessible via Docker / cloud).
3. **PowerShell** (Windows) or terminal (Linux/macOS).

---

## 6. Local Setup and Installation (Windows PowerShell)

### Step 1: Open Terminal in Project Directory
```powershell
cd "c:\infosys Internship\resume-parsing-api"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> *Tip: If you encounter an execution policy error in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before activating.*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 7. PostgreSQL Database Configuration

### Step 1: Create Database in PostgreSQL
Using `psql` or pgAdmin:
```sql
CREATE DATABASE resume_parser_db;
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Update your `.env` file with your PostgreSQL credentials:
```env
# PostgreSQL connection string (psycopg 3 driver)
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/resume_parser_db

# Storage settings
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=5

# Application environment
APP_ENV=development
HOST=127.0.0.1
PORT=8000
```

### Step 3: Run Database Migrations
Apply the initial database schema using Alembic:
```powershell
alembic upgrade head
```

---

## 8. Starting the Application

Run the server with **Uvicorn** and auto-reload enabled:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Alternative Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 9. API Endpoints Reference

All resume endpoints are routed under `/api/v1/resumes`.

| Method | Endpoint | Description | Success Status | Error Statuses |
|---|---|---|---|---|
| `POST` | `/api/v1/resumes/parse` | Upload and parse a PDF or DOCX resume | `201 Created` | 400, 413, 415, 422, 500 |
| `GET` | `/api/v1/resumes/{resume_id}` | Retrieve parsed resume details by ID | `200 OK` | 404, 500 |
| `GET` | `/api/v1/resumes` | List parsed resumes with pagination | `200 OK` | 500 |
| `DELETE` | `/api/v1/resumes/{resume_id}` | Delete resume record and stored file | `204 No Content`| 404, 500 |
| `GET` | `/health` | Check service & DB connectivity | `200 OK` | - |

---

## 10. Sample Requests and Responses

### 1. Upload and Parse Resume (`POST /api/v1/resumes/parse`)

**curl Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/parse" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_resumes/sample_resume.pdf"
```

**Response (`201 Created`):**
```json
{
  "message": "Resume uploaded and parsed successfully",
  "resume_id": 1,
  "filename": "sample_resume.pdf",
  "file_type": "pdf",
  "extracted_data": {
    "full_name": "Arun Kumar",
    "email": "arun.kumar@example.com",
    "phone": "+91 9876543210",
    "address": "Hyderabad, Telangana",
    "linkedin": "https://www.linkedin.com/in/arunkumar-dev",
    "github": "https://github.com/arunkumar-code",
    "professional_summary": "Computer Science graduate with deep passion for backend web development and cloud technologies. Seeking an opportunity to build scalable RESTful APIs.",
    "skills": [
      "Python", "FastAPI", "Django", "Flask", "Java", "PostgreSQL",
      "MySQL", "Redis", "Docker", "Git", "REST", "Communication", "Teamwork"
    ],
    "technical_skills": [
      "Python", "Java", "FastAPI", "Django", "Flask", "PostgreSQL", "MySQL", "Redis", "Docker", "Git", "REST"
    ],
    "soft_skills": [
      "Communication", "Teamwork", "Problem Solving"
    ],
    "education": [
      {
        "degree": "B.Tech in Computer Science and Engineering",
        "institution": "Jawaharlal Nehru Technological University",
        "year": "2020 - 2024",
        "details": "8.5 / 10"
      }
    ],
    "work_experience": [
      {
        "company": "Tech Solutions Inc",
        "role": "Software Engineer",
        "dates": "Jan 2024 - Present",
        "description": "Developed high performance microservices using FastAPI and PostgreSQL. Automated container deployment pipelines with Docker and GitHub Actions."
      }
    ],
    "projects": [
      {
        "name": "Resume Parsing API",
        "description": "Built a production-ready REST API to automatically extract resume information into structured JSON.",
        "technologies": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "PyMuPDF"]
      }
    ],
    "certifications": [
      {
        "name": "AWS Certified Solutions Architect Associate (2023)",
        "issuer": "AWS",
        "year": "2023",
        "details": ""
      },
      {
        "name": "Infosys Springboard Python Professional Certificate (2024)",
        "issuer": "Infosys",
        "year": "2024",
        "details": ""
      }
    ],
    "internships": [
      {
        "organization": "Cloud Innovations",
        "role": "Backend Developer Intern",
        "dates": "Jun 2023 - Dec 2023",
        "description": "Assisted in building REST APIs and query optimization for relational databases."
      }
    ],
    "languages": [
      "English", "Hindi", "Telugu"
    ],
    "achievements": [
      "First place in National University Hackathon 2023.",
      "Published technical paper on distributed API rate-limiting algorithms."
    ],
    "other_information": []
  }
}
```

---

### 2. Get Parsed Resume (`GET /api/v1/resumes/{resume_id}`)

**curl Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/resumes/1" -H "accept: application/json"
```

**Response (`200 OK`):**
```json
{
  "resume_id": 1,
  "original_filename": "sample_resume.pdf",
  "stored_filename": "9b1deb4d3b7d4f89ac3f86130d5a013d.pdf",
  "file_type": "pdf",
  "file_size": 28412,
  "extracted_data": { ... },
  "created_at": "2026-10-30T20:25:00.123456Z",
  "updated_at": "2026-10-30T20:25:00.123456Z"
}
```

---

### 3. List Parsed Resumes (`GET /api/v1/resumes?page=1&page_size=10`)

**curl Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/resumes?page=1&page_size=10" -H "accept: application/json"
```

**Response (`200 OK`):**
```json
{
  "items": [
    {
      "resume_id": 1,
      "filename": "sample_resume.pdf",
      "file_type": "pdf",
      "full_name": "Arun Kumar",
      "uploaded_at": "2026-10-30T20:25:00.123456Z"
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1
}
```

---

### 4. Delete Parsed Resume (`DELETE /api/v1/resumes/{resume_id}`)

**curl Request:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/resumes/1"
```

**Response:**
`HTTP 204 No Content`

---

### 5. Health Check (`GET /health`)

**curl Request:**
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 11. Error Handling & Standard Error Codes

The API returns consistent JSON error envelopes:
```json
{
  "detail": "Descriptive human-readable error message"
}
```

| Scenario | Status Code | Detail Example |
|---|---|---|
| Empty File | `400 Bad Request` | `"The uploaded file is empty."` |
| Nonexistent Resume | `404 Not Found` | `"Resume with ID 99 not found."` |
| File Size Limit Exceeded | `413 Content Too Large` | `"The uploaded file exceeds the maximum allowed size of 5 MB."` |
| Unsupported Extension / Mime | `415 Unsupported Media Type` | `"Unsupported file format '.txt'. Upload a PDF or DOCX file."` |
| Corrupt or Scanned PDF (No Text) | `422 Unprocessable Entity` | `"The PDF contains no extractable text. The document may be empty, corrupted, or composed of scanned images requiring Optical Character Recognition (OCR)."` |
| Database Failure | `500 Internal Server Error` | `"Database error while saving parsed resume record."` |

---

## 12. Running Automated Tests

Run the full pytest suite with verbose output:
```powershell
.\.venv\Scripts\pytest -v
```

### Test Suite Summary:
- **`tests/test_resume_upload.py`**:
  - `test_health_check`: verifies health check reports correct status and DB state.
  - `test_successful_pdf_upload`: verifies valid PDF upload and extraction.
  - `test_successful_docx_upload`: verifies valid DOCX upload and extraction.
  - `test_empty_file_upload`: validates 400 rejection for 0-byte files.
  - `test_unsupported_file_extension`: validates 415 rejection for non-PDF/DOCX extensions.
  - `test_invalid_pdf_signature`: validates 415 rejection when file extension is .pdf but lacks `%PDF-` header.
  - `test_invalid_docx_signature`: validates 415 rejection when file extension is .docx but lacks valid zip archive header.
  - `test_blank_pdf_no_extractable_text`: validates 422 error advising OCR for scanned/blank PDFs.
  - `test_oversized_file_upload`: validates 413 rejection when file exceeds size limit.
- **`tests/test_resume_extraction.py`**:
  - `test_candidate_name_extraction`: candidate name extraction from top lines.
  - `test_candidate_name_ignores_resume_title_and_contacts`: ignores "Resume", "CV", emails, phones.
  - `test_email_extraction`: RFC email pattern extraction.
  - `test_phone_extraction`: Indian mobile numbers and international numbers (rejection of years).
  - `test_linkedin_and_github_extraction`: normalization of social links.
  - `test_skills_categorization`: categorization into technical skills and soft skills.
  - `test_education_extraction`: structured degree, institution, year, details.
  - `test_projects_extraction`: project title, descriptions, and technology list.
  - `test_missing_fields_defaults`: verifies null for missing scalar fields and `[]` for missing list fields.
- **`tests/test_resume_database.py`**:
  - `test_resume_persistence_and_retrieval`: round-trip upload, database storage, and retrieval by ID.
  - `test_get_nonexistent_resume`: 404 response for invalid ID.
  - `test_resume_listing_and_pagination`: page, page_size, total, and item summaries.
  - `test_resume_deletion_lifecycle`: record deletion and filesystem file removal.
  - `test_delete_nonexistent_resume`: 404 response when deleting missing ID.

**Current Test Result: 23 passed in ~1.17s (100% pass rate).**

---

## 13. Privacy and Security Considerations

1. **Path Traversal Protection**: Uploaded files are renamed using secure random `UUID4` hexadecimal strings. The original filename is stored strictly as metadata in the database and never used directly on the filesystem.
2. **File Signature Checking**: Extensions alone are never trusted; files must pass magic-byte checks (`%PDF-` for PDF, OpenXML zip format for DOCX).
3. **Sensitive Data Redaction**: Database credentials, passwords, and server absolute paths are never returned in client API error responses.
4. **Data Isolation**: Files are stored in a dedicated `uploads/` directory that is excluded from Git tracking via `.gitignore`.
5. **Disk File Cleanup**: In case of database failure during parsing, newly saved files on disk are automatically deleted to prevent orphaned storage leaks.

---

## 14. Current Limitations of Rule-Based Extraction

- **Scanned Resumes**: Rule-based extraction extracts digital text layers. Resumes that are scanned images or photographs of paper resumes do not contain selectable text and require Optical Character Recognition (OCR). The API clearly returns HTTP 422 in such cases.
- **Complex Multi-Column Tables**: Extreme multi-column or non-standard graphical resume layouts (e.g., resumes created in graphic design tools with random text boxes) may alter the reading flow of extracted text.
- **Non-Standard Section Headings**: Unconventional section headers (e.g., "What I Love Doing") may be grouped under "Other Information" rather than "Experience" or "Skills".

---

## 15. Future Extensibility

The service architecture is modular and decoupled to allow future upgrades without breaking the API contract:
1. **OCR Integration**: Plug in Tesseract or Amazon Textract in `app/services/pdf_service.py` for image-based PDFs.
2. **LLM / NLP Extraction**: Introduce an optional NLP extractor (e.g. spaCy or LLM) behind the same `ExtractedResumeData` schema interface.
3. **Resume Scoring & Quality Analysis**: Add endpoints to score resume keyword density against specific job descriptions.
4. **Resume Export / Reformatting**: Generate formatted HTML/PDF resumes from parsed JSON.

---

## 16. Git Version Control Instructions

To initialize the repository and publish to your GitHub account:

```powershell
# 1. Initialize git repository
git init

# 2. Add all project files
git add .

# 3. Commit initial implementation
git commit -m "feat: complete Resume Parsing API with FastAPI, PostgreSQL, PyMuPDF, and python-docx"

# 4. Set default branch to main
git branch -M main

# 5. Add your remote repository (replace with your GitHub repository URL)
# git remote add origin https://github.com/<your-username>/resume-parsing-api.git

# 6. Push to GitHub
# git push -u origin main
```
