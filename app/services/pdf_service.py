"""PDF text extraction service using PyMuPDF (fitz)."""

import logging
from typing import Union
from pathlib import Path
import pymupdf as fitz
from app.exceptions import DocumentExtractionException

logger = logging.getLogger(__name__)


class PDFService:
    """Service for safely extracting text from PDF documents."""

    @staticmethod
    def extract_text(source: Union[str, Path, bytes]) -> str:
        """Extract plain text from all pages of a PDF document in page order.
        
        Args:
            source: File path (str/Path) or raw bytes of the PDF.

        Returns:
            Extracted combined text.

        Raises:
            DocumentExtractionException: If the PDF is corrupted, password-protected,
            or contains no extractable text.
        """
        doc = None
        try:
            if isinstance(source, bytes):
                doc = fitz.open(stream=source, filetype="pdf")
            else:
                doc = fitz.open(str(source))

            # Handle password protection / encryption
            if doc.is_encrypted:
                logger.warning("PDF document is password-protected and cannot be parsed.")
                raise DocumentExtractionException(
                    "Password-protected PDFs cannot be extracted. Please upload an unprotected file."
                )

            page_texts = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                if text:
                    page_texts.append(text.strip())

            combined_text = "\n\n".join(page_texts).strip()

            if not combined_text:
                logger.warning("PDF document yielded zero extractable text.")
                raise DocumentExtractionException(
                    "The PDF contains no extractable text. The document may be empty, "
                    "corrupted, or composed of scanned images requiring Optical Character Recognition (OCR)."
                )

            return combined_text

        except DocumentExtractionException:
            raise
        except Exception as exc:
            logger.error("PyMuPDF failed to process PDF: %s", str(exc))
            raise DocumentExtractionException(
                "Unable to extract text from the uploaded PDF document. The file may be corrupt or malformed."
            )
        finally:
            if doc is not None:
                doc.close()
