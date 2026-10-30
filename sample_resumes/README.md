# Sample Resumes Directory

This directory is intended for sample resume files (PDF and DOCX) for manual testing and demonstration.

## Guidelines
- Do NOT commit real personal resumes or sensitive personal contact information into this repository.
- Use synthetic or anonymized candidate resumes for testing and demonstrations.
- Programmatic sample fixtures are automatically generated in automated tests under `tests/` without requiring external files.

## Testing with Sample Files
You can upload sample files through Swagger UI (`http://127.0.0.1:8000/docs`) or via `curl`:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resumes/parse" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_resumes/sample_resume.pdf"
```
