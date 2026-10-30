"""Custom application exceptions."""

from typing import Optional


class ResumeParsingException(Exception):
    """Base exception for resume parsing application."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidFileFormatException(ResumeParsingException):
    """Raised when an uploaded file format is not supported (HTTP 415)."""

    def __init__(self, message: str = "Unsupported file format. Upload a PDF or DOCX file."):
        super().__init__(message=message, status_code=415)


class FileEmptyException(ResumeParsingException):
    """Raised when an uploaded file has a size of 0 bytes (HTTP 400)."""

    def __init__(self, message: str = "The uploaded file is empty."):
        super().__init__(message=message, status_code=400)


class FileSizeExceededException(ResumeParsingException):
    """Raised when an uploaded file exceeds the maximum allowed size (HTTP 413)."""

    def __init__(self, message: str = "The uploaded file exceeds the maximum allowed size."):
        super().__init__(message=message, status_code=413)


class DocumentExtractionException(ResumeParsingException):
    """Raised when text extraction from PDF or DOCX fails (HTTP 422)."""

    def __init__(self, message: str = "Unable to extract text from the uploaded document."):
        super().__init__(message=message, status_code=422)


class ResumeNotFoundException(ResumeParsingException):
    """Raised when a requested resume record is not found in the database (HTTP 404)."""

    def __init__(self, resume_id: Optional[int] = None, message: Optional[str] = None):
        msg = message or (f"Resume with ID {resume_id} not found." if resume_id else "Resume not found.")
        super().__init__(message=msg, status_code=404)


class DatabaseOperationException(ResumeParsingException):
    """Raised when a database error occurs (HTTP 500)."""

    def __init__(self, message: str = "A database error occurred while processing the request."):
        super().__init__(message=message, status_code=500)
