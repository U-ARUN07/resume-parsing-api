"""Unit tests for rule-based information extraction logic."""

from app.services.extraction_service import ResumeExtractor, parse_resume_text


def test_candidate_name_extraction():
    """Test extracting clean candidate name from top lines."""
    text = """Priya Sharma
Hyderabad, India
Email: priya@example.com
Phone: +91 9123456780

SUMMARY
Backend Engineer with 2 years of experience.
"""
    extracted = parse_resume_text(text)
    assert extracted.full_name == "Priya Sharma"


def test_candidate_name_ignores_resume_title_and_contacts():
    """Test that headings like 'RESUME' and contact lines are not treated as candidate names."""
    text = """CURRICULUM VITAE
contact@example.com
+91 9876543210
Rahul Verma
Bengaluru, Karnataka

SKILLS
Python, Django
"""
    extracted = parse_resume_text(text)
    assert extracted.full_name == "Rahul Verma"


def test_email_extraction():
    """Test valid email extraction with varied formats."""
    text = "Please reach out to deepak.singh_99@subdomain.example.co.in for queries."
    extracted = parse_resume_text(text)
    assert extracted.email == "deepak.singh_99@subdomain.example.co.in"


def test_phone_extraction():
    """Test phone extraction for Indian mobile formats and rejecting years."""
    text_indian = "Contact: +91 98765 43210. Graduated in 2021-2025."
    extracted = parse_resume_text(text_indian)
    assert extracted.phone is not None
    assert "98765" in extracted.phone
    assert "2021" not in extracted.phone

    text_intl = "Tel: (555) 123-4567. Project 2024."
    extracted_intl = parse_resume_text(text_intl)
    assert extracted_intl.phone is not None
    assert "123-4567" in extracted_intl.phone


def test_linkedin_and_github_extraction():
    """Test extraction and normalization of LinkedIn and GitHub profiles."""
    text = """
    Profiles:
    LinkedIn: linkedin.com/in/john-doe-engineer
    GitHub: https://github.com/johndoe-dev
    """
    extracted = parse_resume_text(text)
    assert extracted.linkedin == "https://www.linkedin.com/in/john-doe-engineer"
    assert extracted.github == "https://github.com/johndoe-dev"


def test_skills_categorization():
    """Test technical vs soft skills categorization."""
    text = """
    SKILLS
    Python, FastAPI, Docker, PostgreSQL, Communication, Teamwork, Leadership, AWS
    """
    extracted = parse_resume_text(text)
    assert "Python" in extracted.technical_skills
    assert "FastAPI" in extracted.technical_skills
    assert "Docker" in extracted.technical_skills
    assert "PostgreSQL" in extracted.technical_skills
    assert "Communication" in extracted.soft_skills
    assert "Teamwork" in extracted.soft_skills
    assert "Leadership" in extracted.soft_skills


def test_education_extraction():
    """Test structured education item extraction."""
    text = """
    EDUCATION
    B.Tech in Computer Science and Engineering
    Indian Institute of Technology Madras
    2019 - 2023
    CGPA: 8.9 / 10
    """
    extracted = parse_resume_text(text)
    assert len(extracted.education) >= 1
    edu = extracted.education[0]
    assert "B.Tech" in edu.degree
    assert "Technology" in edu.institution or "Institute" in edu.institution
    assert "2019" in edu.year


def test_projects_extraction():
    """Test extraction of projects and associated technologies."""
    text = """
    PROJECTS
    E-Commerce API Service
    Designed and implemented microservices architecture for order management.
    Technologies: Python, FastAPI, Redis, PostgreSQL
    """
    extracted = parse_resume_text(text)
    assert len(extracted.projects) >= 1
    proj = extracted.projects[0]
    assert "E-Commerce" in proj.name
    assert "FastAPI" in proj.technologies
    assert "PostgreSQL" in proj.technologies


def test_missing_fields_defaults():
    """Ensure missing fields are returned as None (scalar) or [] (lists) without fabricating info."""
    bare_text = """John Doe
john@example.com
"""
    extracted = parse_resume_text(bare_text)
    assert extracted.full_name == "John Doe"
    assert extracted.email == "john@example.com"
    # Missing scalar fields must be None
    assert extracted.phone is None
    assert extracted.address is None
    assert extracted.linkedin is None
    assert extracted.github is None
    assert extracted.professional_summary is None
    # Missing list fields must be empty lists
    assert extracted.skills == []
    assert extracted.technical_skills == []
    assert extracted.soft_skills == []
    assert extracted.education == []
    assert extracted.work_experience == []
    assert extracted.projects == []
    assert extracted.certifications == []
    assert extracted.internships == []
    assert extracted.languages == []
    assert extracted.achievements == []
    assert extracted.other_information == []
