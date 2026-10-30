"""Pydantic schemas for data validation, serialization, and OpenAPI documentation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# -----------------------------------------------------------------------------
# Structured Items within Resume
# -----------------------------------------------------------------------------

class EducationItem(BaseModel):
    """Structured education item extracted from a resume."""
    degree: Optional[str] = Field(default=None, description="Degree or program title (e.g. B.Tech, M.S.)")
    institution: Optional[str] = Field(default=None, description="Name of college or university")
    year: Optional[str] = Field(default=None, description="Graduation year or date range (e.g. 2024 or 2020-2024)")
    details: Optional[str] = Field(default="", description="GPA, coursework, honors, or other details")


class WorkExperienceItem(BaseModel):
    """Structured work experience item extracted from a resume."""
    company: Optional[str] = Field(default=None, description="Employer or company name")
    role: Optional[str] = Field(default=None, description="Job title or designation")
    dates: Optional[str] = Field(default=None, description="Employment dates or tenure")
    description: Optional[str] = Field(default="", description="Key responsibilities and accomplishments")


class ProjectItem(BaseModel):
    """Structured project item extracted from a resume."""
    name: Optional[str] = Field(default=None, description="Project title or name")
    description: Optional[str] = Field(default="", description="Summary of project goals and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies, languages, or tools used")


class CertificationItem(BaseModel):
    """Structured certification item extracted from a resume."""
    name: Optional[str] = Field(default=None, description="Certification title")
    issuer: Optional[str] = Field(default=None, description="Issuing organization or platform")
    year: Optional[str] = Field(default=None, description="Issue date or year")
    details: Optional[str] = Field(default="", description="Credential ID or additional notes")


class InternshipItem(BaseModel):
    """Structured internship item extracted from a resume."""
    organization: Optional[str] = Field(default=None, description="Host organization or company")
    role: Optional[str] = Field(default=None, description="Internship title or role")
    dates: Optional[str] = Field(default=None, description="Internship dates or duration")
    description: Optional[str] = Field(default="", description="Summary of internship tasks and deliverables")


# -----------------------------------------------------------------------------
# Full Extracted Resume Data Schema
# -----------------------------------------------------------------------------

class ExtractedResumeData(BaseModel):
    """Complete structured JSON representation of extracted resume information."""
    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(default=None, description="Extracted candidate full name")
    email: Optional[str] = Field(default=None, description="Extracted candidate email address")
    phone: Optional[str] = Field(default=None, description="Extracted candidate phone number")
    address: Optional[str] = Field(default=None, description="Extracted candidate location or address")
    linkedin: Optional[str] = Field(default=None, description="Normalized LinkedIn profile URL")
    github: Optional[str] = Field(default=None, description="Normalized GitHub profile URL")
    professional_summary: Optional[str] = Field(default=None, description="Professional summary or career objective")
    skills: List[str] = Field(default_factory=list, description="All identified skills normalized and deduplicated")
    technical_skills: List[str] = Field(default_factory=list, description="Technical tools, languages, and frameworks")
    soft_skills: List[str] = Field(default_factory=list, description="Identified interpersonal and professional soft skills")
    education: List[EducationItem] = Field(default_factory=list, description="List of education records")
    work_experience: List[WorkExperienceItem] = Field(default_factory=list, description="List of professional work experiences")
    projects: List[ProjectItem] = Field(default_factory=list, description="List of personal and academic projects")
    certifications: List[CertificationItem] = Field(default_factory=list, description="List of certifications")
    internships: List[InternshipItem] = Field(default_factory=list, description="List of internship experiences")
    languages: List[str] = Field(default_factory=list, description="Spoken/written natural languages")
    achievements: List[str] = Field(default_factory=list, description="List of awards, honors, and achievements")
    other_information: List[str] = Field(default_factory=list, description="Relevant information from other sections")


# -----------------------------------------------------------------------------
# API Request / Response Schemas
# -----------------------------------------------------------------------------

class ResumeUploadResponse(BaseModel):
    """Response returned upon successful upload and parsing of a resume."""
    message: str = Field(default="Resume uploaded and parsed successfully", description="Status message")
    resume_id: int = Field(..., description="Unique database identifier for the parsed resume")
    filename: str = Field(..., description="Original filename uploaded by the user")
    file_type: str = Field(..., description="Detected file type ('pdf' or 'docx')")
    extracted_data: ExtractedResumeData = Field(..., description="Parsed resume information in structured format")


class ResumeDetailResponse(BaseModel):
    """Detailed response returned when fetching an individual resume by ID."""
    resume_id: int = Field(..., description="Resume database ID")
    original_filename: str = Field(..., description="Original uploaded filename")
    stored_filename: str = Field(..., description="Internal storage filename")
    file_type: str = Field(..., description="File extension ('pdf' or 'docx')")
    file_size: int = Field(..., description="File size in bytes")
    extracted_data: ExtractedResumeData = Field(..., description="Structured extracted resume data")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last updated timestamp")


class ResumeListItem(BaseModel):
    """Compact summary item representing a resume in a paginated list."""
    resume_id: int = Field(..., description="Resume database ID")
    filename: str = Field(..., description="Original uploaded filename")
    file_type: str = Field(..., description="File type ('pdf' or 'docx')")
    full_name: Optional[str] = Field(default=None, description="Candidate name extracted from resume")
    uploaded_at: datetime = Field(..., description="Timestamp when resume was uploaded")


class ResumeListResponse(BaseModel):
    """Paginated response containing resume summaries and metadata."""
    items: List[ResumeListItem] = Field(default_factory=list, description="List of resume items for current page")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total count of resumes available")


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="healthy", description="Application operational status")
    database: str = Field(..., description="Database connectivity status ('connected' or 'disconnected')")
    version: str = Field(default="1.0.0", description="API version")
    environment: str = Field(..., description="Current deployment environment")


class ErrorResponse(BaseModel):
    """Standardized error response schema."""
    detail: str = Field(..., description="Human-readable explanation of the error")
