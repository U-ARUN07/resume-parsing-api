"""Tests for database persistence, retrieval, pagination, and deletion."""

from fastapi.testclient import TestClient


def test_resume_persistence_and_retrieval(client: TestClient, sample_pdf_bytes: bytes):
    """Test that uploaded resume is persisted and can be retrieved by ID."""
    files = {"file": ("test_resume.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/v1/resumes/parse", files=files)
    assert upload_res.status_code == 201
    resume_id = upload_res.json()["resume_id"]

    # Retrieve by ID
    get_res = client.get(f"/api/v1/resumes/{resume_id}")
    assert get_res.status_code == 200
    data = get_res.json()

    assert data["resume_id"] == resume_id
    assert data["original_filename"] == "test_resume.pdf"
    assert data["file_type"] == "pdf"
    assert data["file_size"] > 0
    assert "stored_filename" in data
    assert "created_at" in data

    extracted = data["extracted_data"]
    assert extracted["full_name"] == "Arun Kumar"
    assert extracted["email"] == "arun.kumar@example.com"


def test_get_nonexistent_resume(client: TestClient):
    """Test retrieving a nonexistent resume ID returns HTTP 404."""
    response = client.get("/api/v1/resumes/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_resume_listing_and_pagination(client: TestClient, sample_pdf_bytes: bytes):
    """Test listing resumes with pagination metadata."""
    # Upload 3 resumes
    for i in range(3):
        files = {"file": (f"candidate_{i}.pdf", sample_pdf_bytes, "application/pdf")}
        res = client.post("/api/v1/resumes/parse", files=files)
        assert res.status_code == 201

    # Fetch page 1 with page_size=2
    list_res = client.get("/api/v1/resumes?page=1&page_size=2")
    assert list_res.status_code == 200
    data = list_res.json()

    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 3
    assert len(data["items"]) == 2

    first_item = data["items"][0]
    assert "resume_id" in first_item
    assert "filename" in first_item
    assert "file_type" in first_item
    assert "uploaded_at" in first_item
    assert first_item["full_name"] == "Arun Kumar"

    # Fetch page 2
    page2_res = client.get("/api/v1/resumes?page=2&page_size=2")
    assert page2_res.status_code == 200
    page2_data = page2_res.json()
    assert len(page2_data["items"]) >= 1


def test_resume_deletion_lifecycle(client: TestClient, sample_pdf_bytes: bytes):
    """Test deleting an existing resume removes DB record and subsequent retrieval returns 404."""
    files = {"file": ("to_delete.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/v1/resumes/parse", files=files)
    assert upload_res.status_code == 201
    resume_id = upload_res.json()["resume_id"]

    # Delete resume
    del_res = client.delete(f"/api/v1/resumes/{resume_id}")
    assert del_res.status_code == 204

    # Subsequent GET must return 404
    get_res = client.get(f"/api/v1/resumes/{resume_id}")
    assert get_res.status_code == 404


def test_delete_nonexistent_resume(client: TestClient):
    """Test deleting a nonexistent resume returns HTTP 404."""
    response = client.delete("/api/v1/resumes/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
