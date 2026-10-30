"""Main FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import Base, engine
from app.exceptions import ResumeParsingException
from app.routers.resume import router as resume_router
from app.utils.file_utils import ensure_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("resume_parsing_api")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to ensure prerequisite directories and tables."""
    # Ensure upload directory exists
    ensure_directory(settings.upload_path)
    logger.info("Upload directory initialized at: %s", settings.upload_path)

    # Initialize tables if configured or in development/test
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified.")
    except Exception as exc:
        logger.warning(
            "Could not automatically initialize tables (PostgreSQL might be offline or using migrations): %s",
            str(exc),
        )

    yield


app = FastAPI(
    title="Resume Parsing API",
    description=(
        "Infosys Springboard Virtual Internship Program 7.0 — Assignment 2\n\n"
        "A robust, rule-based Resume Parsing REST API that accepts resumes in PDF and DOCX "
        "formats, extracts candidate information, transforms it into structured JSON, "
        "and persists the records into a PostgreSQL database.\n\n"
        "Built with FastAPI, PyMuPDF, python-docx, SQLAlchemy 2.x, and Pydantic 2."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# -----------------------------------------------------------------------------
# Global Exception Handlers
# -----------------------------------------------------------------------------

@app.exception_handler(ResumeParsingException)
async def resume_parsing_exception_handler(request: Request, exc: ResumeParsingException):
    """Handle domain-specific resume parsing exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation error", "errors": exc.errors()},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard Starlette / FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler to prevent leaking internal tracebacks."""
    logger.error("Unhandled server exception: %s", str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing your request."},
    )


# -----------------------------------------------------------------------------
# Root Endpoint
# -----------------------------------------------------------------------------

@app.get(
    "/",
    include_in_schema=False,
    summary="Root Redirect to Swagger Documentation",
)
def root():
    """Redirect root path to interactive Swagger UI documentation."""
    return RedirectResponse(url="/docs")


# -----------------------------------------------------------------------------
# Include Routers
# -----------------------------------------------------------------------------

app.include_router(resume_router)
