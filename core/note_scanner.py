"""
VLM-based OCR for notes processing in Qupled.
Uses Vision Language Models to extract text from lecture notes PDFs/images.

Unlike exercise_scanner which extracts structured exercises,
note_scanner does simple OCR - extracting raw text for chunking/RAG.
"""

from pathlib import Path
from typing import List

try:
    from PIL import Image  # noqa: F401

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from pdf2image import convert_from_path

    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import fitz  # PyMuPDF

    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

__all__ = [
    "scan_notes",
    "scan_image",
    "NoteScannerError",
]


class NoteScannerError(Exception):
    """Raised when VLM API call fails for notes OCR."""

    pass


# System prompt for VLM
NOTE_OCR_SYSTEM = """You are a document OCR specialist. Extract all text accurately while preserving structure and mathematical notation."""

# Prompt for VLM-based notes OCR (simpler than exercise extraction)
NOTE_OCR_PROMPT = """Extract ALL text from these document pages.

RULES:
- Preserve exact text content
- Use LaTeX for math: $inline$ or $$block$$
- Maintain paragraph breaks and structure
- Include headers, bullet points, numbered lists
- Ignore page numbers, headers/footers, watermarks
- Output plain text (no JSON, no markdown code blocks)

Return the extracted text directly."""


def get_pdf_page_count(pdf_path: Path) -> int:
    """Get the number of pages in a PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Number of pages in the PDF

    Raises:
        FileNotFoundError: If PDF not found
        ImportError: If PyMuPDF not installed
    """
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF required. Install: pip install pymupdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def render_page_to_image(pdf_path: Path, page_num: int, dpi: int = 150) -> bytes:
    """Render a single PDF page to PNG image bytes.

    Args:
        pdf_path: Path to PDF file
        page_num: Page number (1-indexed)
        dpi: Resolution for rendering

    Returns:
        PNG image bytes
    """
    if not PDF2IMAGE_AVAILABLE:
        raise ImportError("pdf2image not available. Install: pip install pdf2image")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    import io

    images = convert_from_path(
        pdf_path,
        first_page=page_num,
        last_page=page_num,
        dpi=dpi,
    )

    if not images:
        raise ValueError(f"Page {page_num} not found in PDF")

    buf = io.BytesIO()
    images[0].save(buf, format="PNG")
    return buf.getvalue()


def _resize_image_if_needed(image_bytes: bytes, max_size: int = 2048) -> bytes:
    """Resize image if either dimension exceeds max_size."""
    if not PIL_AVAILABLE:
        return image_bytes

    import io

    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size

    if width <= max_size and height <= max_size:
        return image_bytes

    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _call_vlm_for_ocr(images: List[bytes]) -> str:
    """Call VLM API for OCR.

    Args:
        images: List of page images as bytes

    Returns:
        Extracted text from all pages

    Raises:
        NoteScannerError: If API call fails
    """
    import base64
    import logging

    import requests

    from config import Config

    logger = logging.getLogger(__name__)

    if not images:
        return ""

    # Resize images to reduce API costs
    resized_images = [_resize_image_if_needed(img, max_size=2048) for img in images]

    # Build multi-image content for OpenRouter API
    content = [{"type": "text", "text": NOTE_OCR_PROMPT}]
    for img_bytes in resized_images:
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })

    # Call OpenRouter API
    api_key = Config.OPENROUTER_API_KEY
    if not api_key:
        raise NoteScannerError("OPENROUTER_API_KEY not configured")

    model = Config.OPENROUTER_VLM_MODEL

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": NOTE_OCR_SYSTEM},
                    {"role": "user", "content": content},
                ],
                "temperature": 0.1,
                "max_tokens": 8000,
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise NoteScannerError(f"API call failed: {e}")

    result = response.json()

    try:
        text = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise NoteScannerError(f"Unexpected API response format: {e}")

    logger.info(f"VLM OCR: extracted {len(text)} chars from {len(images)} page(s)")
    return text.strip()


def scan_notes(pdf_path: Path, batch_size: int = 10) -> str:
    """Extract text from a PDF using VLM OCR.

    Processes pages in batches to handle large documents efficiently.

    Args:
        pdf_path: Path to PDF file
        batch_size: Number of pages per VLM call (default 10)

    Returns:
        Extracted text from all pages

    Raises:
        FileNotFoundError: If PDF not found
        NoteScannerError: If OCR fails
    """
    import logging

    logger = logging.getLogger(__name__)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    total_pages = get_pdf_page_count(pdf_path)
    logger.info(f"Scanning {total_pages} pages from {pdf_path.name}")

    all_text = []

    for batch_start in range(0, total_pages, batch_size):
        batch_end = min(batch_start + batch_size, total_pages)
        logger.info(f"Processing pages {batch_start + 1}-{batch_end}")

        # Render batch of pages to images
        batch_images = []
        for page_num in range(batch_start + 1, batch_end + 1):
            img_bytes = render_page_to_image(pdf_path, page_num, dpi=150)
            batch_images.append(img_bytes)

        # Call VLM for OCR
        batch_text = _call_vlm_for_ocr(batch_images)
        if batch_text:
            all_text.append(batch_text)

    full_text = "\n\n".join(all_text)
    logger.info(f"Total extracted: {len(full_text)} chars from {total_pages} pages")
    return full_text


def scan_image(image_path: Path) -> str:
    """Extract text from a single image using VLM OCR.

    Args:
        image_path: Path to image file (PNG, JPG, JPEG)

    Returns:
        Extracted text

    Raises:
        FileNotFoundError: If image not found
        ValueError: If unsupported format
        NoteScannerError: If OCR fails
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    suffix = image_path.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg"}:
        raise ValueError(f"Unsupported image format: {suffix}. Use PNG or JPG.")

    image_bytes = image_path.read_bytes()
    return _call_vlm_for_ocr([image_bytes])
