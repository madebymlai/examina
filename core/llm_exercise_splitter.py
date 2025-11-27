"""
LLM-powered exercise splitting for Examina.
Uses LLM to accurately identify exercise boundaries in PDFs.
"""

import json
import logging
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from core.pdf_processor import PDFContent, PDFPage
from core.exercise_splitter import Exercise, ExerciseSplitter
from models.llm_manager import LLMManager

logger = logging.getLogger(__name__)


# System prompt for exercise detection (language-agnostic)
SYSTEM_PROMPT = """You are an expert at analyzing academic documents in ANY language. Your task is to identify individual exercises/problems in exam papers, homework sheets, and exercise collections.

IMPORTANT RULES:
1. An exercise is a COMPLETE problem that a student needs to solve
2. Sub-questions (a, b, c or i, ii, iii or 1.1, 1.2) belong to their PARENT exercise - do NOT split them
3. Instructions, headers, and administrative text are NOT exercises
4. Look for "--- Page N ---" markers to identify page numbers
5. Copy exercise markers EXACTLY as they appear in the document (any language)

You must return ONLY valid JSON, no explanations."""


USER_PROMPT_TEMPLATE = """Analyze this academic document and identify each distinct exercise/problem.

For each exercise, provide:
- exercise_number: The numeric identifier only (e.g., "1", "2", "3")
- page: The page number where the exercise STARTS (look at "--- Page N ---" markers)
- marker: The EXACT exercise marker text as it appears in the document (copy it verbatim)
- line_hint: Approximate line number within the page (1 = top of page, estimate based on position)

IMPORTANT:
- The "marker" must be the exact text from the document (any language)
- Include the full marker with its number (e.g., "Esercizio 3", "Exercise 3", "問題 3", "3.")
- Do NOT translate or modify the marker - copy it exactly as written
- line_hint helps disambiguate when the same marker appears multiple times on a page

DOCUMENT:
---
{text}
---

Return a JSON object with this exact structure:
{{
  "exercises": [
    {{"exercise_number": "1", "page": 1, "marker": "<exact marker from document>", "line_hint": 5}},
    {{"exercise_number": "2", "page": 3, "marker": "<exact marker from document>", "line_hint": 1}}
  ],
  "total_count": 2,
  "notes": "any observations about the document structure"
}}

If no exercises are found, return: {{"exercises": [], "total_count": 0, "notes": "reason"}}"""


@dataclass
class ExerciseBoundary:
    """Detected exercise boundary from LLM (page-aware)."""
    exercise_number: str
    page: int
    marker: str
    line_hint: int = 1  # Approximate line number for disambiguation
    # Position fields populated by marker search
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None


class LLMExerciseSplitter:
    """LLM-powered exercise boundary detection."""

    def __init__(self, llm_manager: Optional[LLMManager] = None, provider: str = "deepseek"):
        """Initialize LLM exercise splitter.

        Args:
            llm_manager: Existing LLMManager instance (optional)
            provider: LLM provider to use if creating new manager
        """
        self.llm = llm_manager or LLMManager(provider=provider)
        self.regex_fallback = ExerciseSplitter()
        self.exercise_counter = 0

    def split_pdf_content(self, pdf_content: PDFContent, course_code: str) -> List[Exercise]:
        """Split PDF content into individual exercises using LLM.

        Args:
            pdf_content: Extracted PDF content
            course_code: Course code for ID generation

        Returns:
            List of extracted exercises
        """
        self.exercise_counter = 0

        # Combine all pages into single text with page markers
        full_text, page_map = self._prepare_text_with_markers(pdf_content)

        if not full_text.strip():
            logger.warning("Empty PDF content, no exercises to extract")
            return []

        try:
            # Step 1: Get exercise boundaries from LLM (page + marker)
            boundaries = self._detect_boundaries_with_llm(full_text, pdf_content)

            if not boundaries:
                logger.info("LLM found no exercises, falling back to regex")
                return self.regex_fallback.split_pdf_content(pdf_content, course_code)

            # Step 2: Find actual positions in pages using marker search
            boundaries = self._find_boundaries_in_pages(
                boundaries, pdf_content, full_text, page_map
            )

            if not boundaries:
                logger.info("Could not find any markers, falling back to regex")
                return self.regex_fallback.split_pdf_content(pdf_content, course_code)

            # Step 3: Calculate end positions (start of next exercise)
            self._calculate_end_positions(boundaries, len(full_text))

            # Step 4: Extract exercises based on boundaries
            exercises = self._extract_exercises(
                full_text, boundaries, page_map, pdf_content, course_code
            )

            logger.info(f"LLM extracted {len(exercises)} exercises from PDF")
            return exercises

        except Exception as e:
            logger.warning(f"LLM exercise splitting failed: {e}, falling back to regex")
            return self.regex_fallback.split_pdf_content(pdf_content, course_code)

    def _prepare_text_with_markers(self, pdf_content: PDFContent) -> tuple[str, Dict[int, int]]:
        """Combine all pages into single text with position tracking.

        Args:
            pdf_content: PDF content with pages

        Returns:
            Tuple of (combined text, page_map mapping char positions to page numbers)
        """
        text_parts = []
        page_map = {}  # char_position -> page_number
        current_pos = 0

        for page in pdf_content.pages:
            page_text = page.text.strip()
            if page_text:
                # Track where this page starts
                page_map[current_pos] = page.page_number

                # Add page marker for context (LLM can see page breaks)
                if text_parts:
                    text_parts.append(f"\n\n--- Page {page.page_number} ---\n\n")
                    current_pos += len(f"\n\n--- Page {page.page_number} ---\n\n")

                text_parts.append(page_text)
                current_pos += len(page_text)

        return "".join(text_parts), page_map

    def _find_boundaries_in_pages(
        self,
        boundaries: List[ExerciseBoundary],
        pdf_content: PDFContent,
        full_text: str,
        page_map: Dict[int, int]
    ) -> List[ExerciseBoundary]:
        """Find actual positions of exercise markers in page text.

        Uses line_hint to disambiguate when marker appears multiple times.

        Args:
            boundaries: Exercise boundaries from LLM (positions not yet set)
            pdf_content: PDF content with pages
            full_text: Combined document text
            page_map: Mapping of positions to page numbers

        Returns:
            List of boundaries with start_pos set
        """
        found_boundaries = []

        for boundary in boundaries:
            page_idx = boundary.page - 1  # 0-indexed
            if page_idx < 0 or page_idx >= len(pdf_content.pages):
                logger.warning(f"Invalid page index {page_idx} for exercise {boundary.exercise_number}")
                continue

            page = pdf_content.pages[page_idx]
            page_text = page.text

            # Find ALL occurrences of marker on page
            positions = self._find_all_marker_positions(page_text, boundary.marker)

            if len(positions) == 0:
                # Enhanced fuzzy search before giving up
                pos = self._fuzzy_search_marker(page_text, boundary.marker, boundary.exercise_number)
                if pos is not None:
                    positions = [pos]

            if len(positions) == 1:
                pos = positions[0]
            elif len(positions) > 1:
                # Use line_hint to pick the right one
                pos = self._select_by_line_hint(page_text, positions, boundary.line_hint)
            else:
                logger.warning(
                    f"Could not find marker '{boundary.marker}' on page {boundary.page} "
                    f"for exercise {boundary.exercise_number}"
                )
                continue

            # Convert page-relative position to full-text position
            page_start = self._get_page_start_in_fulltext(boundary.page, page_map, full_text)
            boundary.start_pos = page_start + pos
            found_boundaries.append(boundary)

        # Sort by start position
        found_boundaries.sort(key=lambda b: b.start_pos or 0)

        return found_boundaries

    def _find_all_marker_positions(self, text: str, marker: str) -> List[int]:
        """Find all occurrences of a marker in text.

        Args:
            text: Text to search in
            marker: Marker to find

        Returns:
            List of positions where marker was found
        """
        import re
        import unicodedata

        positions = []

        # Strategy 1: Exact match (all occurrences)
        pos = 0
        while True:
            idx = text.find(marker, pos)
            if idx == -1:
                break
            positions.append(idx)
            pos = idx + 1

        if positions:
            return positions

        # Strategy 2: Case-insensitive
        text_lower = text.lower()
        marker_lower = marker.lower()
        pos = 0
        while True:
            idx = text_lower.find(marker_lower, pos)
            if idx == -1:
                break
            positions.append(idx)
            pos = idx + 1

        if positions:
            return positions

        # Strategy 3: Normalize whitespace and search
        text_norm = re.sub(r'\s+', ' ', text)
        marker_norm = re.sub(r'\s+', ' ', marker)
        pos = 0
        while True:
            idx = text_norm.lower().find(marker_norm.lower(), pos)
            if idx == -1:
                break
            # Approximate position in original text
            first_word = marker_norm.lower().split()[0] if marker_norm.split() else marker_norm.lower()
            orig_pos = text.lower().find(first_word, pos)
            if orig_pos >= 0:
                positions.append(orig_pos)
            pos = idx + 1

        return positions

    def _fuzzy_search_marker(self, text: str, marker: str, exercise_number: str) -> Optional[int]:
        """Enhanced fuzzy search for marker with multiple fallback strategies.

        Language-agnostic: Uses the LLM-provided marker directly, no hardcoded patterns.

        Args:
            text: Text to search in
            marker: Marker to find
            exercise_number: Exercise number for pattern matching

        Returns:
            Position if found, None otherwise
        """
        import re
        import unicodedata

        # Strategy 1: Unicode normalization (handles accents, ligatures)
        text_nfc = unicodedata.normalize('NFC', text)
        marker_nfc = unicodedata.normalize('NFC', marker)
        pos = text_nfc.lower().find(marker_nfc.lower())
        if pos >= 0:
            return pos

        # Strategy 2: Build dynamic regex from marker tokens (language-agnostic)
        # E.g., "Esercizio 3" → r'Esercizio\s+3', "問題 5" → r'問題\s+5'
        tokens = marker.split()
        if len(tokens) >= 2:
            # Allow flexible whitespace between tokens
            pattern = r'\s+'.join(re.escape(t) for t in tokens)
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.start()

        # Strategy 3: Find by exercise number only (last resort)
        # Extract any number from marker and search for it at word boundary
        ex_num_match = re.search(r'\d+', marker)
        if ex_num_match:
            ex_num = ex_num_match.group()
            # Look for number preceded by any word and followed by boundary
            # This is language-agnostic: matches "Esercizio 3", "Exercise 3", "問題 3", etc.
            pattern = rf'\b\w+\s+{ex_num}\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.start()

        # Strategy 4: Try just the exercise number with various patterns
        if exercise_number:
            patterns = [
                rf'(?:^|\n)\s*{re.escape(exercise_number)}[\.\)\]:]',  # "3." or "3)" at line start
                rf'\b{re.escape(exercise_number)}\b',  # Just the number
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.MULTILINE)
                if match:
                    return match.start()

        return None

    def _select_by_line_hint(self, text: str, positions: List[int], line_hint: int) -> int:
        """Select position closest to expected line number.

        Args:
            text: Text to analyze
            positions: List of candidate positions
            line_hint: Expected line number (1-indexed)

        Returns:
            Position closest to line_hint
        """
        def get_line_number(pos: int) -> int:
            return text[:pos].count('\n') + 1

        # Find position closest to line_hint
        return min(positions, key=lambda p: abs(get_line_number(p) - line_hint))

    def _get_page_start_in_fulltext(self, page_num: int, page_map: Dict[int, int], full_text: str) -> int:
        """Get the starting position of a page in the full text.

        Args:
            page_num: Page number (1-indexed)
            page_map: Mapping of char positions to page numbers
            full_text: Full document text

        Returns:
            Character position where the page starts
        """
        # Find the position where this page starts
        for pos, pnum in sorted(page_map.items()):
            if pnum == page_num:
                return pos

        # If not found in map, estimate based on page markers
        import re
        pattern = rf'--- Page {page_num} ---'
        match = re.search(pattern, full_text)
        if match:
            # Return position after the marker
            return match.end()

        return 0

    def _calculate_end_positions(self, boundaries: List[ExerciseBoundary], text_length: int) -> None:
        """Calculate end positions for each exercise boundary.

        End position is the start of the next exercise, or end of text.

        Args:
            boundaries: List of boundaries (must be sorted by start_pos)
            text_length: Total length of the text
        """
        for i, boundary in enumerate(boundaries):
            if i + 1 < len(boundaries):
                # End is start of next exercise
                boundary.end_pos = boundaries[i + 1].start_pos
            else:
                # Last exercise ends at end of text
                boundary.end_pos = text_length

    def _detect_boundaries_with_llm(self, text: str, pdf_content: PDFContent) -> List[ExerciseBoundary]:
        """Use LLM to detect exercise boundaries in text.

        Args:
            text: Full document text with page markers
            pdf_content: PDF content for page validation

        Returns:
            List of detected exercise boundaries (positions not yet set)
        """
        # Truncate very long texts to avoid token limits
        max_chars = 50000  # ~12,500 tokens
        if len(text) > max_chars:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {max_chars}")
            text = text[:max_chars]

        # Build prompt
        prompt = USER_PROMPT_TEMPLATE.format(text=text)

        # Call LLM
        logger.info("Calling LLM for exercise boundary detection...")
        response = self.llm.generate(
            prompt=prompt,
            system=SYSTEM_PROMPT,
            temperature=0.1,  # Low temperature for consistent output
            json_mode=True,
            max_tokens=4096
        )

        if not response.success:
            logger.error(f"LLM call failed: {response.error}")
            raise RuntimeError(f"LLM call failed: {response.error}")

        # Parse JSON response
        result = self._parse_llm_response(response.text, pdf_content)

        return result

    def _parse_llm_response(self, response_text: str, pdf_content: PDFContent) -> List[ExerciseBoundary]:
        """Parse LLM JSON response into exercise boundaries.

        Args:
            response_text: Raw LLM response text
            pdf_content: PDF content for page validation

        Returns:
            List of ExerciseBoundary objects (positions set to None initially)
        """
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            logger.warning("Failed to parse JSON directly, trying extraction")
            try:
                # Look for JSON object in response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            except Exception as e:
                logger.error(f"Failed to parse LLM response: {e}")
                raise

        exercises_data = data.get("exercises", [])
        if not exercises_data:
            logger.info(f"LLM found no exercises. Notes: {data.get('notes', 'none')}")
            return []

        logger.info(f"LLM detected {data.get('total_count', len(exercises_data))} exercises")

        max_page = len(pdf_content.pages)
        boundaries = []

        for ex in exercises_data:
            page = ex.get("page", 1)

            # Validate page number
            if page < 1 or page > max_page:
                logger.warning(f"Invalid page {page} for exercise {ex.get('exercise_number')}, skipping")
                continue

            boundary = ExerciseBoundary(
                exercise_number=str(ex.get("exercise_number", "")),
                page=page,
                marker=ex.get("marker", ""),
                line_hint=ex.get("line_hint", 1),
            )

            if not boundary.marker:
                logger.warning(f"No marker for exercise {boundary.exercise_number}, skipping")
                continue

            boundaries.append(boundary)

        # Sort by page, then line_hint
        boundaries.sort(key=lambda b: (b.page, b.line_hint))

        return boundaries

    def _extract_exercises(
        self,
        full_text: str,
        boundaries: List[ExerciseBoundary],
        page_map: Dict[int, int],
        pdf_content: PDFContent,
        course_code: str
    ) -> List[Exercise]:
        """Extract exercise objects from detected boundaries.

        Args:
            full_text: Combined document text
            boundaries: Detected exercise boundaries
            page_map: Mapping of positions to page numbers
            pdf_content: Original PDF content
            course_code: Course code

        Returns:
            List of Exercise objects
        """
        exercises = []

        for i, boundary in enumerate(boundaries):
            # Determine text range
            start_pos = boundary.start_pos or 0

            # End is either the specified end or start of next exercise
            if boundary.end_pos:
                end_pos = boundary.end_pos
            elif i + 1 < len(boundaries) and boundaries[i + 1].start_pos:
                end_pos = boundaries[i + 1].start_pos
            else:
                end_pos = len(full_text)

            # Extract text
            exercise_text = full_text[start_pos:end_pos].strip()

            # Clean up page markers from text
            exercise_text = self._clean_text(exercise_text)

            if not exercise_text or len(exercise_text) < 20:
                logger.warning(f"Skipping empty/short exercise {boundary.exercise_number}")
                continue

            # Determine page number
            page_number = self._get_page_number(start_pos, page_map)

            # Get images from that page
            page_images = []
            for page in pdf_content.pages:
                if page.page_number == page_number and page.images:
                    page_images = page.images
                    break

            # Create exercise
            exercise = self._create_exercise(
                text=exercise_text,
                page_number=page_number,
                exercise_number=boundary.exercise_number,
                images=page_images,
                has_latex=any(p.has_latex for p in pdf_content.pages if p.page_number == page_number),
                source_pdf=pdf_content.file_path.name,
                course_code=course_code
            )

            exercises.append(exercise)

        return exercises

    def _get_page_number(self, char_pos: int, page_map: Dict[int, int]) -> int:
        """Determine page number for a character position.

        Args:
            char_pos: Character position in combined text
            page_map: Mapping of start positions to page numbers

        Returns:
            Page number (1-indexed)
        """
        page_num = 1
        for pos, pnum in sorted(page_map.items()):
            if pos <= char_pos:
                page_num = pnum
            else:
                break
        return page_num

    def _clean_text(self, text: str) -> str:
        """Clean exercise text.

        Args:
            text: Raw exercise text

        Returns:
            Cleaned text
        """
        import re

        # Remove page markers we added
        text = re.sub(r'\n*--- Page \d+ ---\n*', '\n', text)

        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove page numbers
        text = re.sub(r'(?:^|\n)Pagina\s+\d+(?:\n|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(?:^|\n)Page\s+\d+(?:\n|$)', '', text, flags=re.IGNORECASE)

        return text.strip()

    def _create_exercise(
        self,
        text: str,
        page_number: int,
        exercise_number: Optional[str],
        images: List[bytes],
        has_latex: bool,
        source_pdf: str,
        course_code: str
    ) -> Exercise:
        """Create an Exercise object.

        Args:
            text: Exercise text
            page_number: Page number
            exercise_number: Exercise number/label
            images: Image data
            has_latex: Whether LaTeX was detected
            source_pdf: Source PDF filename
            course_code: Course code

        Returns:
            Exercise object
        """
        self.exercise_counter += 1

        # Generate unique ID
        components = f"{course_code}_{source_pdf}_{page_number}_{exercise_number or 'none'}_{self.exercise_counter}"
        hash_obj = hashlib.md5(components.encode())
        short_hash = hash_obj.hexdigest()[:12]

        course_abbrev = course_code.lower().replace('b', '').replace('0', '')[:6]
        exercise_id = f"{course_abbrev}_{self.exercise_counter:04d}_{short_hash}"

        return Exercise(
            id=exercise_id,
            text=text,
            page_number=page_number,
            exercise_number=exercise_number,
            has_images=len(images) > 0,
            image_data=images,
            has_latex=has_latex,
            latex_content=None,
            source_pdf=source_pdf
        )


# Convenience function for one-off splitting
def split_pdf_with_llm(pdf_content: PDFContent, course_code: str, provider: str = "deepseek") -> List[Exercise]:
    """Split PDF content using LLM.

    Args:
        pdf_content: PDF content to split
        course_code: Course code
        provider: LLM provider

    Returns:
        List of exercises
    """
    splitter = LLMExerciseSplitter(provider=provider)
    return splitter.split_pdf_content(pdf_content, course_code)
