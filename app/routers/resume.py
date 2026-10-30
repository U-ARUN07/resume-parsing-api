"""FastAPI router for resume parsing and management endpoints."""

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db, check_database_connection
from app.config import get_settings
from app.schemas import (
    ResumeUploadResponse,
    ResumeDetailResponse,
    ResumeListResponse,
    HealthCheckResponse,
    ErrorResponse,
)
from app.services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()
settings = get_settings()


# -----------------------------------------------------------------------------
# Endpoint 1: Upload and Parse Resume
# -----------------------------------------------------------------------------
@router.post(
    "/api/v1/resumes/parse",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and Parse Resume",
    description=(
        "Accept a PDF or DOCX resume file, extract its text, perform rule-based "
        "information extraction to convert candidate details into structured JSON, "
        "store the file and extracted record in the database, and return the structured data."
    ),
    responses={
        201: {"description": "Resume uploaded and parsed successfully", "model": ResumeUploadResponse},
        400: {"description": "Empty file uploaded", "model": ErrorResponse},
        413: {"description": "File exceeds maximum allowed upload size (5 MB)", "model": ErrorResponse},
        415: {"description": "Unsupported file format. Must be PDF or DOCX", "model": ErrorResponse},
        422: {"description": "Unable to extract text from document", "model": ErrorResponse},
        500: {"description": "Internal database or processing error", "model": ErrorResponse},
    },
    tags=["Resume Parsing"],
)
async def upload_and_parse_resume(
    file: UploadFile = File(
        ...,
        description="Resume file in PDF (.pdf) or Microsoft Word (.docx) format",
    ),
    db: Session = Depends(get_db),
):
    """Upload a resume file (PDF or DOCX), parse and persist structured candidate details."""
    return await resume_service.parse_and_store_resume(file, db)


# -----------------------------------------------------------------------------
# Endpoint 2: Get Parsed Resume by ID
# -----------------------------------------------------------------------------
@router.get(
    "/api/v1/resumes/{resume_id}",
    response_model=ResumeDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Parsed Resume",
    description="Retrieve a previously parsed resume record and its structured JSON by database ID.",
    responses={
        200: {"description": "Parsed resume details retrieved successfully", "model": ResumeDetailResponse},
        404: {"description": "Resume not found", "model": ErrorResponse},
    },
    tags=["Resume Parsing"],
)
def get_parsed_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve an individual resume record by primary key."""
    return resume_service.get_resume(resume_id, db)


# -----------------------------------------------------------------------------
# Endpoint 3: List Parsed Resumes (Paginated)
# -----------------------------------------------------------------------------
@router.get(
    "/api/v1/resumes",
    response_model=ResumeListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Parsed Resumes",
    description="Return a paginated list of uploaded resumes with metadata and extracted candidate names.",
    responses={
        200: {"description": "Paginated resume list retrieved successfully", "model": ResumeListResponse},
    },
    tags=["Resume Parsing"],
)
def list_parsed_resumes(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number (1-indexed)",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of resumes to return per page (max 100)",
    ),
    db: Session = Depends(get_db),
):
    """List parsed resumes with pagination."""
    return resume_service.list_resumes(page=page, page_size=page_size, db=db)


# -----------------------------------------------------------------------------
# Endpoint 4: Delete Parsed Resume
# -----------------------------------------------------------------------------
@router.delete(
    "/api/v1/resumes/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Parsed Resume",
    description=(
        "Permanently delete a parsed resume record from PostgreSQL and remove its "
        "stored file from the filesystem."
    ),
    responses={
        204: {"description": "Resume deleted successfully"},
        404: {"description": "Resume not found", "model": ErrorResponse},
    },
    tags=["Resume Parsing"],
)
def delete_parsed_resume(
    resume_id: int,
    db: Session = Depends(get_db),
):
    """Delete a resume record and associated file."""
    resume_service.delete_resume(resume_id, db)
    return None


# -----------------------------------------------------------------------------
# Endpoint 5: Health Check
# -----------------------------------------------------------------------------
@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    description="Check whether the API service and its database connection are active and healthy.",
    responses={
        200: {"description": "Application status report", "model": HealthCheckResponse},
    },
    tags=["System"],
)
def health_check():
    """Report application health status and database connectivity safely."""
    db_connected = check_database_connection()
    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        database="connected" if db_connected else "disconnected",
        version="1.0.0",
        environment=settings.APP_ENV,
    )
