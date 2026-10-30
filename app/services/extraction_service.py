"""Rule-based Resume Information Extraction Service using Python and Regular Expressions.

Modularly parses unstructured resume text into validated, structured ExtractedResumeData.
"""

import re
from typing import List, Optional, Dict, Tuple
from app.schemas import (
    ExtractedResumeData,
    EducationItem,
    WorkExperienceItem,
    ProjectItem,
    CertificationItem,
    InternshipItem,
)

# -----------------------------------------------------------------------------
# Curated Skill and Keyword Dictionaries
# -----------------------------------------------------------------------------

TECHNICAL_SKILLS_DB = [
    # Languages
    "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript", "Go", "Golang",
    "Rust", "Ruby", "PHP", "Kotlin", "Swift", "Dart", "R", "Scala", "Perl", "Julia",
    "SQL", "PL/SQL", "HTML", "HTML5", "CSS", "CSS3", "Sass", "SCSS", "Bash", "Shell",
    # Frameworks & Libraries
    "FastAPI", "Flask", "Django", "Spring", "Spring Boot", "Express", "Express.js",
    "Node.js", "React", "React.js", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js",
    "ASP.NET", ".NET", ".NET Core", "Ruby on Rails", "Laravel", "Symfony", "NestJS",
    "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Pandas", "NumPy", "Matplotlib",
    "Seaborn", "OpenCV", "NLTK", "Spacy", "HuggingFace", "LangChain", "LlamaIndex",
    # Databases & Caches
    "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "SQLite", "Oracle",
    "Microsoft SQL Server", "MSSQL", "Cassandra", "Elasticsearch", "DynamoDB",
    "Firebase", "Supabase", "Neo4j", "CouchDB", "MariaDB",
    # Cloud, DevOps & Platforms
    "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP", "Google Cloud",
    "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Jenkins", "GitHub Actions",
    "GitLab CI", "CircleCI", "Linux", "Ubuntu", "Debian", "CentOS", "RedHat",
    "Nginx", "Apache", "Kafka", "RabbitMQ", "Celery", "Airflow", "GraphQL", "REST",
    "RESTful API", "Microservices", "Serverless",
    # Tools & Methodologies
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Postman",
    "Swagger", "OpenAPI", "Alembic", "SQLAlchemy", "Hibernate", "Prisma",
]

SOFT_SKILLS_DB = [
    "Communication", "Written Communication", "Verbal Communication",
    "Leadership", "Team Leadership", "Team Management",
    "Teamwork", "Collaboration", "Interpersonal Skills",
    "Problem Solving", "Critical Thinking", "Analytical Skills",
    "Time Management", "Work Ethic", "Adaptability", "Flexibility",
    "Agile", "Scrum", "Kanban", "Creativity", "Innovation",
    "Presentation Skills", "Public Speaking", "Negotiation",
    "Mentoring", "Decision Making", "Active Listening",
    "Conflict Resolution", "Attention to Detail", "Multitasking",
]

NATURAL_LANGUAGES_DB = [
    "English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam",
    "Marathi", "Bengali", "Gujarati", "Punjabi", "Urdu", "Odia",
    "Spanish", "French", "German", "Japanese", "Mandarin", "Chinese",
    "Russian", "Italian", "Portuguese", "Arabic", "Korean",
]

# Section header patterns
SECTION_PATTERNS: Dict[str, List[str]] = {
    "summary": [
        r"professional\s+summary",
        r"career\s+summary",
        r"summary",
        r"career\s+objective",
        r"objective",
        r"profile",
        r"about\s+me",
    ],
    "skills": [
        r"technical\s+skills",
        r"key\s+skills",
        r"core\s+competencies",
        r"skills\s*(?:&|and)\s*technologies",
        r"technologies",
        r"skills\s*(?:&|and)\s*tools",
        r"technical\s+proficiencies",
        r"skills",
    ],
    "experience": [
        r"work\s+experience",
        r"professional\s+experience",
        r"employment\s+history",
        r"employment",
        r"experience",
    ],
    "education": [
        r"educational\s+qualifications",
        r"academic\s+background",
        r"academic\s+qualifications",
        r"education",
        r"academics",
    ],
    "projects": [
        r"academic\s+projects",
        r"personal\s+projects",
        r"key\s+projects",
        r"technical\s+projects",
        r"projects",
    ],
    "certifications": [
        r"licenses\s*(?:&|and)\s*certifications",
        r"certifications",
        r"certificates",
        r"courses\s*(?:&|and)\s*certifications",
    ],
    "internships": [
        r"internship\s+experience",
        r"internships",
        r"industrial\s+training",
    ],
    "languages": [
        r"languages\s+known",
        r"languages",
        r"language\s+proficiency",
    ],
    "achievements": [
        r"awards\s*(?:&|and)\s*achievements",
        r"honors\s*(?:&|and)\s*awards",
        r"achievements",
        r"awards",
        r"honors",
        r"accomplishments",
    ],
    "other": [
        r"extracurricular\s+activities",
        r"extra-curricular\s+activities",
        r"volunteering",
        r"publications",
        r"hobbies\s*(?:&|and)\s*interests",
        r"interests",
    ],
}


# -----------------------------------------------------------------------------
# Modular Extractor Classes
# -----------------------------------------------------------------------------

class ResumeExtractor:
    """Orchestrates rule-based parsing of unstructured resume text."""

    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.clean_text = self._clean_text(raw_text)
        self.lines = [line.strip() for line in self.clean_text.splitlines() if line.strip()]
        self.sections = self._split_into_sections()

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalize line breaks and excessive whitespace while preserving text flow."""
        # Replace carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace non-breaking spaces and tabs
        text = text.replace("\xa0", " ").replace("\t", " ")
        # Remove repeated horizontal whitespace
        text = re.sub(r"[ ]{2,}", " ", text)
        return text

    def _split_into_sections(self) -> Dict[str, str]:
        """Identify section headings and partition the text into section blocks."""
        # Build regex for headings
        all_header_patterns = []
        pattern_to_category: Dict[str, str] = {}
        for category, patterns in SECTION_PATTERNS.items():
            for pat in patterns:
                all_header_patterns.append(pat)
                pattern_to_category[pat] = category

        combined_regex = (
            r"(?im)^[\s#*_-]*(?:" + "|".join(all_header_patterns) + r")[\s*:]*$"
        )

        matches = list(re.finditer(combined_regex, self.clean_text))
        sections: Dict[str, List[str]] = {}

        if not matches:
            return {}

        for i, match in enumerate(matches):
            matched_header = match.group(0).strip().lower()
            matched_header_clean = re.sub(r"[#*_\-:\s]+", " ", matched_header).strip()

            # Determine category
            category = "other"
            for pat, cat in pattern_to_category.items():
                if re.fullmatch(pat, matched_header_clean, re.IGNORECASE):
                    category = cat
                    break

            start_idx = match.end()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(self.clean_text)
            content = self.clean_text[start_idx:end_idx].strip()

            if category not in sections:
                sections[category] = []
            sections[category].append(content)

        return {k: "\n\n".join(v) for k, v in sections.items()}

    def extract_full_name(self) -> Optional[str]:
        """Extract candidate full name from the top lines of the resume."""
        disallowed_name_words = {
            "resume", "curriculum", "vitae", "cv", "bio", "biodata", "profile",
            "summary", "objective", "experience", "education", "skills", "projects",
            "contact", "phone", "email", "address", "engineer", "developer",
            "student", "fresher", "intern", "graduate", "page", "portfolio",
        }

        # Inspect the top 10 lines
        candidate_lines = self.lines[:10]
        for line in candidate_lines:
            # Skip lines containing email, URL, or digits
            if "@" in line or "http" in line or "www." in line or "github.com" in line or "linkedin.com" in line:
                continue
            if re.search(r"\d", line):
                continue
            if ":" in line or "|" in line or "/" in line:
                continue

            cleaned_line = re.sub(r"[^a-zA-Z\s.]", "", line).strip()
            words = cleaned_line.split()

            # Names are usually 2 to 4 words
            if 2 <= len(words) <= 4:
                lower_words = {w.lower().rstrip(".") for w in words}
                if any(w in disallowed_name_words for w in lower_words):
                    continue

                # Check if words look like proper nouns (title-case or upper-case)
                if all(w.isupper() or w[0].isupper() for w in words if len(w) > 1):
                    # Format nicely in Title Case
                    return " ".join(word.capitalize() for word in words)

        return None

    def extract_email(self) -> Optional[str]:
        """Extract first valid email address."""
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, self.clean_text)
        return match.group(0).strip().lower() if match else None

    def extract_phone(self) -> Optional[str]:
        """Extract phone number, prioritizing Indian and international mobile formats."""
        # Indian numbers with country code or standard formats
        patterns = [
            r"(?:\+91[\s\-]?)?[6-9]\d{4}[\s\-]?\d{5}\b",
            r"(?:\+91[\s\-]?)?[6-9]\d{9}\b",
            r"\+?\d{1,3}[\s\-\.]\(?\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4}\b",
            r"\b\(?\d{3}\)?[\s\-\.]\d{3}[\s\-\.]\d{4}\b",
        ]

        for pat in patterns:
            match = re.search(pat, self.clean_text)
            if match:
                phone_str = match.group(0).strip()
                # Ensure not a graduation year or date range
                digits_only = re.sub(r"\D", "", phone_str)
                if len(digits_only) >= 10:
                    return phone_str
        return None

    def extract_address(self) -> Optional[str]:
        """Extract candidate address or location."""
        # 1. Look for labeled address
        label_pattern = r"(?im)(?:address|location|residence|city|residing\s+at)\s*[:\-]\s*([^\n\r]+)"
        match = re.search(label_pattern, self.clean_text)
        if match:
            candidate = match.group(1).strip()
            # Clean unwanted tokens
            candidate = re.split(r"[|•\t]", candidate)[0].strip()
            if candidate and not ("@" in candidate or "http" in candidate):
                return candidate

        # 2. Look for common Indian city, state combinations
        city_state_pattern = (
            r"\b(Hyderabad|Bengaluru|Bangalore|Chennai|Mumbai|Pune|Delhi|New Delhi|"
            r"Kolkata|Noida|Gurgaon|Gurugram|Ahmedabad|Jaipur|Kochi|Trivandrum|"
            r"Coimbatore|Visakhapatnam|Vijayawada|Mysore|Bhubaneswar)"
            r"(?:,\s*(Telangana|Karnataka|Tamil Nadu|Maharashtra|Delhi|West Bengal|Uttar Pradesh|Haryana|Gujarat|Rajasthan|Kerala|Andhra Pradesh|Odisha))?\b"
        )
        city_match = re.search(city_state_pattern, self.clean_text, re.IGNORECASE)
        if city_match:
            city = city_match.group(1)
            state = city_match.group(2)
            return f"{city}, {state}" if state else city

        return None

    def extract_linkedin(self) -> Optional[str]:
        """Extract and normalize LinkedIn profile URL."""
        pattern = r"(?:https?:\/\/)?(?:[a-zA-Z0-9-]+\.)?linkedin\.com\/in\/([a-zA-Z0-9_\-]+)\/?"
        match = re.search(pattern, self.clean_text, re.IGNORECASE)
        if match:
            slug = match.group(1)
            return f"https://www.linkedin.com/in/{slug}"
        return None

    def extract_github(self) -> Optional[str]:
        """Extract and normalize GitHub profile URL."""
        pattern = r"(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_\-]+)\/?"
        matches = re.finditer(pattern, self.clean_text, re.IGNORECASE)
        for match in matches:
            username = match.group(1)
            if username.lower() not in {"topics", "features", "explore", "about", "pricing", "login", "join"}:
                return f"https://github.com/{username}"
        return None

    def extract_professional_summary(self) -> Optional[str]:
        """Extract summary or career objective."""
        summary = self.sections.get("summary")
        if summary:
            # Clean bullets and excessive blank lines
            lines = [re.sub(r"^[\s*•\-–>]+", "", line).strip() for line in summary.splitlines() if line.strip()]
            cleaned = " ".join(lines)
            return cleaned if cleaned else None
        return None

    def extract_skills(self) -> Tuple[List[str], List[str], List[str]]:
        """Extract technical skills, soft skills, and combined overall skills."""
        found_tech: Dict[str, str] = {}
        found_soft: Dict[str, str] = {}
        found_all: Dict[str, str] = {}

        # Scan text for technical skills
        for skill in TECHNICAL_SKILLS_DB:
            pattern = r"(?i)(?<![\w#+])" + re.escape(skill) + r"(?![\w#+])"
            if re.search(pattern, self.clean_text):
                found_tech[skill.lower()] = skill
                found_all[skill.lower()] = skill

        # Scan text for soft skills
        for skill in SOFT_SKILLS_DB:
            pattern = r"(?i)\b" + re.escape(skill) + r"\b"
            if re.search(pattern, self.clean_text):
                found_soft[skill.lower()] = skill
                found_all[skill.lower()] = skill

        # Parse dedicated Skills section if present
        skills_section = self.sections.get("skills", "")
        if skills_section:
            # Split items by comma, semicolon, bullet, newline, pipe
            tokens = re.split(r"[,;•|•\n\r/]+", skills_section)
            for raw_token in tokens:
                token = re.sub(r"^[\s*•\-–>]+", "", raw_token).strip()
                # Ignore tokens that are labels like "Languages:", "Databases:"
                token = re.sub(r"^[A-Za-z\s]+:\s*", "", token).strip()
                if 2 <= len(token) <= 40 and not re.search(r"https?://|@", token):
                    key = token.lower()
                    if key not in found_all:
                        found_all[key] = token

        return (
            list(found_all.values()),
            list(found_tech.values()),
            list(found_soft.values()),
        )

    def extract_education(self) -> List[EducationItem]:
        """Extract structured education items."""
        edu_section = self.sections.get("education", "")
        search_text = edu_section if edu_section else self.clean_text

        items: List[EducationItem] = []

        # Degree patterns
        degree_patterns = [
            r"\b(B\.?Tech(?:nology)?|B\.?E\.?|Bachelor\s+of\s+Technology|Bachelor\s+of\s+Engineering)\b",
            r"\b(M\.?Tech(?:nology)?|M\.?E\.?|Master\s+of\s+Technology|Master\s+of\s+Engineering)\b",
            r"\b(B\.?Sc(?:ience)?|Bachelor\s+of\s+Science|BCA|Bachelor\s+of\s+Computer\s+Applications)\b",
            r"\b(M\.?Sc(?:ience)?|Master\s+of\s+Science|MCA|Master\s+of\s+Computer\s+Applications|M\.?S\.?)\b",
            r"\b(MBA|Master\s+of\s+Business\s+Administration|BBA)\b",
            r"\b(Ph\.?D\.?|Doctor\s+of\s+Philosophy)\b",
            r"\b(Intermediate|Higher\s+Secondary|Class\s+XII|Class\s+X|High\s+School)\b",
        ]

        # Year patterns
        year_pattern = r"\b(19\d{2}|20\d{2})\s*(?:-|–|to)?\s*(19\d{2}|20\d{2}|Present|Current)?\b"
        # Institution keywords
        inst_pattern = r"([A-Z][A-Za-z0-9\s&,.'-]{3,60}(?:University|Institute|College|Academy|School|Campus|Vidyalaya|Polytechnic))"
        # Details pattern (GPA / Percentage)
        details_pattern = r"(?:(?:CGPA|GPA|Percentage|Marks)[\s:]*([0-9.]+(?:\s*\/\s*10|\s*\/\s*4|\s*%)?))"

        # Split education section into blocks by blank lines or group by degree
        raw_blocks = re.split(r"\n\s*\n", search_text.strip())
        blocks: List[str] = []
        for rb in raw_blocks:
            lines = [l.strip() for l in rb.splitlines() if l.strip()]
            current_group: List[str] = []
            for l in lines:
                is_deg = any(re.search(d_pat, l, re.IGNORECASE) for d_pat in degree_patterns)
                if is_deg and current_group:
                    blocks.append("\n".join(current_group))
                    current_group = [l]
                else:
                    current_group.append(l)
            if current_group:
                blocks.append("\n".join(current_group))

        for block in blocks:
            degree_found = None
            for d_pat in degree_patterns:
                m = re.search(d_pat, block, re.IGNORECASE)
                if m:
                    degree_found = m.group(0).strip()
                    break

            if degree_found:
                # Find institution
                inst_match = re.search(inst_pattern, block, re.IGNORECASE)
                institution = inst_match.group(1).strip() if inst_match else None

                # Find year
                year_match = re.search(year_pattern, block, re.IGNORECASE)
                year = year_match.group(0).strip() if year_match else None

                # Find details
                details_match = re.search(details_pattern, block, re.IGNORECASE)
                details = details_match.group(0).strip() if details_match else ""

                items.append(
                    EducationItem(
                        degree=degree_found,
                        institution=institution,
                        year=year,
                        details=details,
                    )
                )

        return items

    def extract_work_experience(self) -> List[WorkExperienceItem]:
        """Extract professional work experience."""
        exp_section = self.sections.get("experience", "")
        if not exp_section:
            return []

        items: List[WorkExperienceItem] = []
        date_pattern = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.]+\d{4}\s*(?:-|–|to)\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.]+\d{4}|\d{4})\b|\b(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:Present|Current|(?:19|20)\d{2})\b"

        blocks = re.split(r"\n\s*\n", exp_section)
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            # Skip if explicitly internship
            if any(re.search(r"\bintern(?:ship)?\b", l, re.IGNORECASE) for l in lines[:2]):
                continue

            header_line = lines[0]
            date_match = re.search(date_pattern, header_line, re.IGNORECASE)
            dates = date_match.group(0).strip() if date_match else None

            # Look for company/role
            role = None
            company = None
            desc_lines = []

            # Check standard separators (e.g. "Software Engineer | Google" or "Google - Software Engineer")
            if "|" in header_line:
                parts = [p.strip() for p in header_line.split("|")]
                role = parts[0]
                company = parts[1] if len(parts) > 1 else None
            elif " - " in header_line or " – " in header_line:
                parts = re.split(r"\s+[-–]\s+", header_line)
                role = parts[0]
                company = parts[1] if len(parts) > 1 else None
            else:
                role = header_line

            # Rest are descriptions
            for line in lines[1:]:
                # If date wasn't on line 0, check line 1
                if not dates:
                    d_m = re.search(date_pattern, line, re.IGNORECASE)
                    if d_m:
                        dates = d_m.group(0).strip()
                        continue
                desc_lines.append(re.sub(r"^[\s*•\-–>]+", "", line).strip())

            items.append(
                WorkExperienceItem(
                    company=company,
                    role=role,
                    dates=dates,
                    description=" ".join(desc_lines),
                )
            )

        return items

    def extract_internships(self) -> List[InternshipItem]:
        """Extract internships."""
        intern_section = self.sections.get("internships", "")
        items: List[InternshipItem] = []

        date_pattern = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.]+\d{4}\s*(?:-|–|to)\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s.]+\d{4}|\d{4})\b|\b(?:19|20)\d{2}\s*(?:-|–|to)\s*(?:Present|Current|(?:19|20)\d{2})\b"

        # Search in internships section
        if intern_section:
            blocks = re.split(r"\n\s*\n", intern_section)
            for block in blocks:
                lines = [l.strip() for l in block.splitlines() if l.strip()]
                if not lines:
                    continue
                header = lines[0]
                date_m = re.search(date_pattern, header, re.IGNORECASE)
                dates = date_m.group(0).strip() if date_m else None

                role = header
                org = None
                if "|" in header:
                    p = [x.strip() for x in header.split("|")]
                    role, org = p[0], p[1]
                elif " at " in header.lower():
                    p = re.split(r"\s+at\s+", header, flags=re.IGNORECASE)
                    role, org = p[0], p[1]

                desc = " ".join(re.sub(r"^[\s*•\-–>]+", "", l).strip() for l in lines[1:])
                items.append(
                    InternshipItem(
                        organization=org,
                        role=role,
                        dates=dates,
                        description=desc,
                    )
                )

        return items

    def extract_projects(self) -> List[ProjectItem]:
        """Extract personal or academic projects."""
        proj_section = self.sections.get("projects", "")
        if not proj_section:
            return []

        items: List[ProjectItem] = []
        blocks = re.split(r"\n\s*\n", proj_section)

        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            name = lines[0]
            technologies: List[str] = []
            desc_lines: List[str] = []

            # Check if title has technologies e.g. "Resume Parser (Python, FastAPI)"
            tech_match = re.search(r"\(([^)]+)\)", name)
            if tech_match:
                tech_str = tech_match.group(1)
                technologies = [t.strip() for t in re.split(r"[,/|]+", tech_str) if t.strip()]
                name = name[:tech_match.start()].strip()

            for line in lines[1:]:
                # Check for "Technologies:", "Tools Used:", "Tech Stack:"
                tech_line_match = re.search(
                    r"(?:technologies|tech\s+stack|tools\s+used|built\s+with)\s*[:\-]\s*(.+)",
                    line,
                    re.IGNORECASE,
                )
                if tech_line_match:
                    tokens = [t.strip() for t in re.split(r"[,/|]+", tech_line_match.group(1)) if t.strip()]
                    technologies.extend(tokens)
                else:
                    desc_lines.append(re.sub(r"^[\s*•\-–>]+", "", line).strip())

            # Deduplicate technologies
            technologies = list(dict.fromkeys(technologies))

            items.append(
                ProjectItem(
                    name=name,
                    description=" ".join(desc_lines),
                    technologies=technologies,
                )
            )

        return items

    def extract_certifications(self) -> List[CertificationItem]:
        """Extract certifications and courses."""
        cert_section = self.sections.get("certifications", "")
        if not cert_section:
            return []

        items: List[CertificationItem] = []
        lines = [l.strip() for l in cert_section.splitlines() if l.strip()]

        known_issuers = ["AWS", "Google", "Microsoft", "Oracle", "IBM", "Infosys", "Cisco", "Coursera", "Udemy", "HackerRank"]
        year_pattern = r"\b(19\d{2}|20\d{2})\b"

        for line in lines:
            cleaned_line = re.sub(r"^[\s*•\-–>]+", "", line).strip()
            if not cleaned_line:
                continue

            # Issuer detection
            issuer = None
            for ki in known_issuers:
                if ki.lower() in cleaned_line.lower():
                    issuer = ki
                    break

            # Year detection
            y_m = re.search(year_pattern, cleaned_line)
            year = y_m.group(0) if y_m else None

            items.append(
                CertificationItem(
                    name=cleaned_line,
                    issuer=issuer,
                    year=year,
                    details="",
                )
            )

        return items

    def extract_languages(self) -> List[str]:
        """Extract natural spoken/written languages."""
        lang_section = self.sections.get("languages", "")
        text_to_search = lang_section if lang_section else self.clean_text

        found_languages = []
        for lang in NATURAL_LANGUAGES_DB:
            pattern = r"(?i)\b" + re.escape(lang) + r"\b"
            if re.search(pattern, text_to_search):
                found_languages.append(lang)

        return found_languages

    def extract_achievements(self) -> List[str]:
        """Extract achievements, honors, and awards."""
        ach_section = self.sections.get("achievements", "")
        if not ach_section:
            return []

        achievements = []
        lines = [l.strip() for l in ach_section.splitlines() if l.strip()]
        for line in lines:
            cleaned = re.sub(r"^[\s*•\-–>]+", "", line).strip()
            if cleaned and len(cleaned) > 5:
                achievements.append(cleaned)
        return achievements

    def extract_other_information(self) -> List[str]:
        """Capture remaining useful items from unclassified sections."""
        other_section = self.sections.get("other", "")
        if not other_section:
            return []

        items = []
        lines = [l.strip() for l in other_section.splitlines() if l.strip()]
        for line in lines:
            cleaned = re.sub(r"^[\s*•\-–>]+", "", line).strip()
            if cleaned and len(cleaned) > 4:
                items.append(cleaned)
        return items

    def parse(self) -> ExtractedResumeData:
        """Execute full extraction pipeline and return validated ExtractedResumeData."""
        all_skills, tech_skills, soft_skills = self.extract_skills()

        return ExtractedResumeData(
            full_name=self.extract_full_name(),
            email=self.extract_email(),
            phone=self.extract_phone(),
            address=self.extract_address(),
            linkedin=self.extract_linkedin(),
            github=self.extract_github(),
            professional_summary=self.extract_professional_summary(),
            skills=all_skills,
            technical_skills=tech_skills,
            soft_skills=soft_skills,
            education=self.extract_education(),
            work_experience=self.extract_work_experience(),
            projects=self.extract_projects(),
            certifications=self.extract_certifications(),
            internships=self.extract_internships(),
            languages=self.extract_languages(),
            achievements=self.extract_achievements(),
            other_information=self.extract_other_information(),
        )


def parse_resume_text(text: str) -> ExtractedResumeData:
    """Convenience functional wrapper to parse resume text."""
    extractor = ResumeExtractor(text)
    return extractor.parse()
