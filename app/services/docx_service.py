"""DOCX text extraction service using python-docx."""

import io
import logging
from typing import Union
from pathlib import Path
import docx
from app.exceptions import DocumentExtractionException

logger = logging.getLogger(__name__)


class DOCXService:
    """Service for safely extracting text from Microsoft Word (.docx) documents."""

    @staticmethod
    def extract_text(source: Union[str, Path, bytes]) -> str:
        """Extract text from paragraphs and tables within a DOCX document.

        Args:
            source: File path (str/Path) or raw bytes of the DOCX document.

        Returns:
            Extracted combined text.

        Raises:
            DocumentExtractionException: If the document is corrupt or contains no extractable text.
        """
        try:
            if isinstance(source, bytes):
                doc_stream = io.BytesIO(source)
                document = docx.Document(doc_stream)
            else:
                document = docx.Document(str(source))

            extracted_chunks = []

            # 1. Extract text from paragraphs
            for paragraph in document.paragraphs:
                text = paragraph.text.strip()
                if text:
                    extracted_chunks.append(text)

            # 2. Extract text from tables (often used for education, skills, and layout)
            for table in document.tables:
                for row in table.rows:
                    row_cells_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    # Deduplicate adjacent cells if merged
                    unique_cells = []
                    for cell_text in row_cells_text:
                        if not unique_cells or cell_text != unique_cells[-1]:
                            unique_cells.append(cell_text)
                    if unique_cells:
                        extracted_chunks.append(" | ".join(unique_cells))

            combined_text = "\n".join(extracted_chunks).strip()

            if not combined_text:
                logger.warning("DOCX document yielded zero extractable text.")
                raise DocumentExtractionException(
                    "The DOCX document contains no extractable text. The file may be blank or corrupted."
                )

            return combined_text

        except DocumentExtractionException:
            raise
        except Exception as exc:
            logger.error("python-docx failed to process document: %s", str(exc))
            raise DocumentExtractionException(
                "Unable to extract text from the uploaded DOCX document. The file may be corrupt or invalid."
            )
