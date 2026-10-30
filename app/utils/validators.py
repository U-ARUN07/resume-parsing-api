"""Validation utilities for file uploads and data integrity."""

import os
import re
import zipfile
import io
from pathlib import Path
from app.config import get_settings
from app.exceptions import (
    InvalidFileFormatException,
    FileEmptyException,
    FileSizeExceededException,
)

PDF_MAGIC_BYTES = b"%PDF-"
ZIP_MAGIC_BYTES = b"PK\x03\x04"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and remove dangerous characters."""
    if not filename:
        return "unnamed_resume"
    # Strip path components
    basename = os.path.basename(filename)
    # Remove null bytes and control chars
    basename = re.sub(r"[\x00-\x1f\x7f]", "", basename)
    # Replace path separators
    basename = basename.replace("/", "").replace("\\", "")
    # Remove leading dots to prevent hidden files
    basename = basename.lstrip(".")
    return basename or "unnamed_resume"


def validate_file_extension(filename: str) -> str:
    """Validate that the filename has a supported extension (.pdf or .docx).
    
    Returns the normalized extension without dot (e.g. 'pdf' or 'docx').
    """
    settings = get_settings()
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise InvalidFileFormatException(
            f"Unsupported file format '{ext}'. Upload a PDF or DOCX file."
        )
    return ext.lstrip(".")


def validate_file_content(content: bytes, file_type: str) -> None:
    """Validate file content, size, and magic bytes signature."""
    settings = get_settings()

    # Check empty
    if len(content) == 0:
        raise FileEmptyException("The uploaded file is empty.")

    # Check size
    if len(content) > settings.max_upload_size_bytes:
        raise FileSizeExceededException(
            f"The uploaded file exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    # Validate signatures
    if file_type == "pdf":
        if not content.startswith(PDF_MAGIC_BYTES):
            raise InvalidFileFormatException(
                "Invalid PDF document: missing standard PDF header signature."
            )
    elif file_type == "docx":
        if not content.startswith(ZIP_MAGIC_BYTES):
            raise InvalidFileFormatException(
                "Invalid DOCX document: file is not a valid OpenXML package."
            )
        # Verify valid zip package structure
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                # DOCX standard package must have word/document.xml or [Content_Types].xml
                namelist = zf.namelist()
                if not any("word/document.xml" in name for name in namelist):
                    raise InvalidFileFormatException(
                        "Invalid DOCX document: missing Word document structure."
                    )
        except zipfile.BadZipFile:
            raise InvalidFileFormatException(
                "Corrupt DOCX document: unable to read package archive."
            )
