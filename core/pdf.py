"""
PDF processing utilities for Qupled.
Basic text extraction using PyMuPDF.

For OCR, use:
- note_scanner.py for notes
- exercise_scanner.py for exercises
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


@dataclass
class PDFPage:
    """Represents a single page from a PDF."""

    page_number: int
    text: str
    images: List[bytes]
    has_latex: bool
    latex_content: Optional[str] = None


@dataclass
class PDFContent:
    """Complete PDF content extraction."""

    file_path: Path
    total_pages: int
    pages: List[PDFPage]
    metadata: Dict[str, Any]


class PDFProcessor:
    """Processes PDF files using PyMuPDF for basic text extraction."""

    def __init__(self):
        """Initialize PDF processor."""
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is required. Install: pip install pymupdf")

    def process_pdf(self, pdf_path: Path) -> PDFContent:
        """Process a PDF file and extract all content.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDFContent with extracted information
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        return self._process_with_pymupdf(pdf_path)

    def _process_with_pymupdf(self, pdf_path: Path) -> PDFContent:
        """Process PDF using PyMuPDF (fitz)."""
        doc = fitz.open(pdf_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text
            text = page.get_text()

            # Extract images
            images = []
            image_list = page.get_images()
            for img in image_list:
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append(image_bytes)
                except Exception:
                    continue

            # Check for LaTeX (simple heuristic)
            has_latex, latex_content = self._detect_latex(text)

            pages.append(
                PDFPage(
                    page_number=page_num + 1,
                    text=text,
                    images=images,
                    has_latex=has_latex,
                    latex_content=latex_content,
                )
            )

        metadata = doc.metadata or {}
        doc.close()

        return PDFContent(
            file_path=pdf_path, total_pages=len(pages), pages=pages, metadata=metadata
        )

    def _detect_latex(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect LaTeX formulas in text."""
        latex_patterns = [
            r"\$.*?\$",
            r"\$\$.*?\$\$",
            r"\\begin\{equation\}.*?\\end\{equation\}",
            r"\\begin\{align\}.*?\\end\{align\}",
            r"\\frac\{.*?\}\{.*?\}",
            r"\\sum",
            r"\\int",
            r"\\alpha",
            r"\\beta",
        ]

        latex_content = []
        has_latex = False

        for pattern in latex_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                has_latex = True
                latex_content.extend(matches)

        if has_latex:
            return True, "\n".join(latex_content[:10])
        return False, None

    def get_pdf_page_count(self, pdf_path: Path) -> int:
        """Get the number of pages in a PDF."""
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count

    def extract_text_from_page(self, pdf_path: Path, page_number: int) -> str:
        """Extract text from a specific page (1-indexed)."""
        doc = fitz.open(pdf_path)
        page = doc[page_number - 1]
        text = page.get_text()
        doc.close()
        return text

    def is_scanned_pdf(self, pdf_path: Path, sample_pages: int = 3) -> bool:
        """Detect if PDF is scanned (image-based) or digital (text-based)."""
        total_pages = self.get_pdf_page_count(pdf_path)
        pages_to_check = min(sample_pages, total_pages)

        text_chars = 0
        for page_num in range(1, pages_to_check + 1):
            text = self.extract_text_from_page(pdf_path, page_num)
            text_chars += len(text.strip())

        avg_chars_per_page = text_chars / pages_to_check if pages_to_check > 0 else 0
        return avg_chars_per_page < 100
