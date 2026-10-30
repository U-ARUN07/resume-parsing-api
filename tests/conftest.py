"""Pytest fixtures and test environment configuration."""

import io
import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest

# Configure test environment variables BEFORE app or database imports
test_db_file = Path(tempfile.gettempdir()) / "resume_parser_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_file}"
os.environ["APP_ENV"] = "testing"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import pymupdf as fitz
import docx

from app.database import Base, get_db
from app.main import app
from app.config import get_settings

SAMPLE_RESUME_TEXT = """Arun Kumar
Hyderabad, Telangana
Email: arun.kumar@example.com
Phone: +91 9876543210
LinkedIn: https://www.linkedin.com/in/arunkumar-dev
GitHub: https://github.com/arunkumar-code

SUMMARY
Computer Science graduate with deep passion for backend web development and cloud technologies. Seeking an opportunity to build scalable RESTful APIs.

SKILLS
Python, Java, FastAPI, Django, Flask, PostgreSQL, MySQL, Redis, Docker, Git, REST, Microservices, Communication, Teamwork, Problem Solving

EDUCATION
B.Tech in Computer Science and Engineering
Jawaharlal Nehru Technological University
2020 - 2024
CGPA: 8.5 / 10

WORK EXPERIENCE
Software Engineer | Tech Solutions Inc
Jan 2024 - Present
Developed high performance microservices using FastAPI and PostgreSQL.
Automated container deployment pipelines with Docker and GitHub Actions.

INTERNSHIPS
Backend Developer Intern at Cloud Innovations
Jun 2023 - Dec 2023
Assisted in building REST APIs and query optimization for relational databases.

PROJECTS
Resume Parsing API
Built a production-ready REST API to automatically extract resume information into structured JSON.
Technologies: Python, FastAPI, SQLAlchemy, PostgreSQL, PyMuPDF

CERTIFICATIONS
AWS Certified Solutions Architect Associate (2023)
Infosys Springboard Python Professional Certificate (2024)

LANGUAGES
English, Hindi, Telugu

ACHIEVEMENTS
First place in National University Hackathon 2023.
Published technical paper on distributed API rate-limiting algorithms.
"""


@pytest.fixture(scope="session")
def sample_resume_text() -> str:
    """Return realistic candidate resume plain text."""
    return SAMPLE_RESUME_TEXT


@pytest.fixture(scope="session")
def sample_pdf_bytes(sample_resume_text: str) -> bytes:
    """Generate a valid, programmatic PDF file using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 60), sample_resume_text, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture(scope="session")
def sample_docx_bytes(sample_resume_text: str) -> bytes:
    """Generate a valid, programmatic DOCX file using python-docx."""
    doc = docx.Document()
    for paragraph in sample_resume_text.split("\n\n"):
        doc.add_paragraph(paragraph)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture(scope="function")
def test_db_session(tmp_path: Path) -> Generator[Session, None, None]:
    """Provide an isolated SQLite database session for each test."""
    db_file = tmp_path / "test_isolated.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db_session: Session, tmp_path: Path) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with overridden database session and upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    settings = get_settings()
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(upload_dir)

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Cleanup
    app.dependency_overrides.clear()
    settings.UPLOAD_DIR = original_upload_dir
