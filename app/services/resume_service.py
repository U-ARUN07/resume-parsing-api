"""Resume business logic service orchestrating file storage, extraction, and database persistence."""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from fastapi import UploadFile

from app.models import Resume
from app.schemas import (
    ExtractedResumeData,
    ResumeUploadResponse,
    ResumeDetailResponse,
    ResumeListItem,
    ResumeListResponse,
)
from app.exceptions import ResumeNotFoundException, DatabaseOperationException
from app.services.file_service import FileService
from app.services.extraction_service import parse_resume_text

logger = logging.getLogger(__name__)


class ResumeService:
    """Service handling high-level resume business operations."""

    def __init__(self, file_service: FileService | None = None):
        self.file_service = file_service or FileService()

    async def parse_and_store_resume(
        self, upload_file: UploadFile, db: Session
    ) -> ResumeUploadResponse:
        """Process uploaded file, extract structured data, and persist to database.

        Ensures atomic persistence and disk cleanup if database insertion fails.
        """
        # Step 1: Save file and extract raw text
        (
            original_filename,
            stored_filename,
            file_type,
            file_path,
            file_size,
            extracted_text,
        ) = await self.file_service.process_and_save_upload(upload_file)

        # Step 2: Perform rule-based structured information extraction
        extracted_data: ExtractedResumeData = parse_resume_text(extracted_text)

        # Step 3: Persist record to PostgreSQL
        try:
            resume_record = Resume(
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_type=file_type,
                file_path=str(file_path),
                file_size=file_size,
                extracted_text=extracted_text,
                extracted_data=extracted_data.model_dump(),
            )
            db.add(resume_record)
            db.commit()
            db.refresh(resume_record)

            logger.info(
                "Successfully persisted resume ID=%d ('%s')",
                resume_record.id,
                original_filename,
            )

            return ResumeUploadResponse(
                message="Resume uploaded and parsed successfully",
                resume_id=resume_record.id,
                filename=resume_record.original_filename,
                file_type=resume_record.file_type,
                extracted_data=extracted_data,
            )

        except Exception as exc:
            db.rollback()
            # Clean up the file created on disk to avoid orphaned files
            self.file_service.delete_stored_file(stored_filename)
            logger.error("Failed to persist resume to database: %s", str(exc))
            raise DatabaseOperationException(
                "Database error while saving parsed resume record."
            )

    def get_resume(self, resume_id: int, db: Session) -> ResumeDetailResponse:
        """Retrieve a parsed resume by its ID."""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResumeNotFoundException(resume_id=resume_id)

        extracted_data_obj = ExtractedResumeData.model_validate(resume.extracted_data)

        return ResumeDetailResponse(
            resume_id=resume.id,
            original_filename=resume.original_filename,
            stored_filename=resume.stored_filename,
            file_type=resume.file_type,
            file_size=resume.file_size,
            extracted_data=extracted_data_obj,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
        )

    def list_resumes(
        self, page: int, page_size: int, db: Session
    ) -> ResumeListResponse:
        """Return a paginated list of resumes with summary metadata."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
        elif page_size > 100:
            page_size = 100

        total = db.scalar(select(func.count(Resume.id))) or 0
        offset = (page - 1) * page_size

        records = (
            db.query(Resume)
            .order_by(Resume.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        items = []
        for rec in records:
            candidate_name = None
            if isinstance(rec.extracted_data, dict):
                candidate_name = rec.extracted_data.get("full_name")

            items.append(
                ResumeListItem(
                    resume_id=rec.id,
                    filename=rec.original_filename,
                    file_type=rec.file_type,
                    full_name=candidate_name,
                    uploaded_at=rec.created_at,
                )
            )

        return ResumeListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def delete_resume(self, resume_id: int, db: Session) -> None:
        """Delete resume record from database and associated stored file from disk."""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ResumeNotFoundException(resume_id=resume_id)

        stored_filename = resume.stored_filename

        try:
            db.delete(resume)
            db.commit()
            logger.info("Deleted resume record ID=%d from database", resume_id)
        except Exception as exc:
            db.rollback()
            logger.error("Failed to delete resume ID=%d: %s", resume_id, str(exc))
            raise DatabaseOperationException("Failed to delete resume record from database.")

        # Safely remove stored file from disk
        self.file_service.delete_stored_file(stored_filename)
