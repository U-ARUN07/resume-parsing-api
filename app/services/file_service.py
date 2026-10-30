"""File storage, validation, and content routing service."""

import logging
from pathlib import Path
from fastapi import UploadFile

from app.config import get_settings
from app.utils.validators import (
    sanitize_filename,
    validate_file_extension,
    validate_file_content,
)
from app.utils.file_utils import (
    ensure_directory,
    generate_unique_filename,
    safe_delete_file,
)
from app.services.pdf_service import PDFService
from app.services.docx_service import DOCXService

logger = logging.getLogger(__name__)


class FileService:
    """Handles file saving, validation, extraction dispatch, and cleanup."""

    def __init__(self):
        pass

    @property
    def settings(self):
        return get_settings()

    @property
    def upload_dir(self) -> Path:
        return ensure_directory(self.settings.upload_path)

    async def process_and_save_upload(self, upload_file: UploadFile) -> tuple[str, str, str, Path, int, str]:
        """Validate, store, and extract text from an uploaded file.
        
        Returns:
            tuple of (clean_original_filename, stored_filename, file_type, file_path, file_size, extracted_text)
        """
        original_name = sanitize_filename(upload_file.filename or "resume")
        file_type = validate_file_extension(original_name)

        # Read file content safely in memory (checked against max size)
        content = await upload_file.read()
        file_size = len(content)

        # Validate content size and magic signature
        validate_file_content(content, file_type)

        # Generate unique storage filename
        stored_filename = generate_unique_filename(file_type)
        destination_path = self.upload_dir / stored_filename

        try:
            # Save file to disk
            destination_path.write_bytes(content)
            logger.info("Saved uploaded file '%s' as '%s'", original_name, stored_filename)

            # Route to appropriate extraction service
            if file_type == "pdf":
                extracted_text = PDFService.extract_text(content)
            elif file_type == "docx":
                extracted_text = DOCXService.extract_text(content)
            else:
                raise ValueError(f"Unhandled file type: {file_type}")

            return (
                original_name,
                stored_filename,
                file_type,
                destination_path,
                file_size,
                extracted_text,
            )

        except Exception:
            # Clean up the stored file if extraction fails
            if destination_path.exists():
                safe_delete_file(destination_path)
            raise

    def delete_stored_file(self, stored_filename: str) -> bool:
        """Delete a file from the upload directory by its stored filename."""
        target_path = self.upload_dir / stored_filename
        return safe_delete_file(target_path)
