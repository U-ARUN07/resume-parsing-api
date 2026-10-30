"""SQLAlchemy 2.x database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
from app.database import Base


class Resume(Base):
    """Resume model storing file metadata and structured extracted resume data."""

    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True, index=True)
    file_type = Column(String(10), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)

    # Use JSON with JSONB fallback for PostgreSQL while remaining compatible with SQLite for tests
    extracted_data = Column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_resumes_file_type_created_at", "file_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, filename='{self.original_filename}', type='{self.file_type}')>"
