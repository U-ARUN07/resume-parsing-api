"""Tests for resume file uploads, validation, and error handling."""

import io
import pymupdf as fitz
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint reports status and database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data
    assert "environment" in data


def test_successful_pdf_upload(client: TestClient, sample_pdf_bytes: bytes):
    """Test successful upload and parsing of a valid PDF resume."""
    files = {
        "file": ("sample_resume.pdf", sample_pdf_bytes, "application/pdf")
    }
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 201
    data = response.json()

    assert data["message"] == "Resume uploaded and parsed successfully"
    assert data["resume_id"] > 0
    assert data["filename"] == "sample_resume.pdf"
    assert data["file_type"] == "pdf"

    extracted = data["extracted_data"]
    assert extracted["full_name"] == "Arun Kumar"
    assert extracted["email"] == "arun.kumar@example.com"
    assert "9876543210" in extracted["phone"]
    assert "Hyderabad" in extracted["address"]
    assert extracted["linkedin"] == "https://www.linkedin.com/in/arunkumar-dev"
    assert extracted["github"] == "https://github.com/arunkumar-code"
    assert "FastAPI" in extracted["technical_skills"]
    assert "Python" in extracted["technical_skills"]
    assert len(extracted["education"]) > 0
    assert len(extracted["projects"]) > 0


def test_successful_docx_upload(client: TestClient, sample_docx_bytes: bytes):
    """Test successful upload and parsing of a valid DOCX resume."""
    files = {
        "file": (
            "sample_resume.docx",
            sample_docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 201
    data = response.json()

    assert data["message"] == "Resume uploaded and parsed successfully"
    assert data["resume_id"] > 0
    assert data["filename"] == "sample_resume.docx"
    assert data["file_type"] == "docx"

    extracted = data["extracted_data"]
    assert extracted["full_name"] == "Arun Kumar"
    assert extracted["email"] == "arun.kumar@example.com"
    assert "Python" in extracted["technical_skills"]


def test_empty_file_upload(client: TestClient):
    """Test upload rejection when file is empty (0 bytes)."""
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_unsupported_file_extension(client: TestClient):
    """Test upload rejection for unsupported file format extension."""
    files = {"file": ("resume.txt", b"Some text content", "text/plain")}
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 415
    assert "unsupported" in response.json()["detail"].lower()


def test_invalid_pdf_signature(client: TestClient):
    """Test rejection when file has .pdf extension but invalid header bytes."""
    files = {"file": ("fake.pdf", b"Not a real PDF file content", "application/pdf")}
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 415
    assert "invalid pdf" in response.json()["detail"].lower()


def test_invalid_docx_signature(client: TestClient):
    """Test rejection when file has .docx extension but invalid zip magic header."""
    files = {"file": ("fake.docx", b"Not a valid docx file", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 415
    assert "invalid docx" in response.json()["detail"].lower()


def test_blank_pdf_no_extractable_text(client: TestClient):
    """Test error handling when a PDF contains no extractable text (e.g. blank page or scanned image)."""
    # Create empty PDF page with no text
    doc = fitz.open()
    doc.new_page()
    blank_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("blank.pdf", blank_bytes, "application/pdf")}
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 422
    assert "ocr" in response.json()["detail"].lower()


def test_oversized_file_upload(client: TestClient, monkeypatch):
    """Test rejection when uploaded file exceeds max allowed size."""
    # Monkeypatch max upload size to 100 bytes for this test
    from app.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 0.0001)  # ~104 bytes

    # Create dummy PDF bytes of ~500 bytes
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "Test payload content to exceed max upload size limit.")
    oversized_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("large.pdf", oversized_bytes, "application/pdf")}
    response = client.post("/api/v1/resumes/parse", files=files)
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()
