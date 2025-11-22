"""
Exercise splitting for Examina.
Splits PDF content into individual exercises based on patterns.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from core.pdf_processor import PDFContent, PDFPage


@dataclass
class Exercise:
    """Represents a single exercise extracted from a PDF."""
    id: str
    text: str
    page_number: int
    exercise_number: Optional[str]
    has_images: bool
    image_data: List[bytes]
    has_latex: bool
    latex_content: Optional[str]
    source_pdf: str


class ExerciseSplitter:
    """Splits PDF content into individual exercises."""

    # Primary patterns - these are most likely to be exercises
    PRIMARY_EXERCISE_PATTERNS = [
        r'(?:^|\n)(?:Esercizio|Exercise|Problema|Problem)\s+(\d+(?:\.\d+)?)',  # Esercizio 1, Exercise 1.2
        r'(?:^|\n)Domanda\s+(\d+)',  # Domanda 1 (Question 1)
        r'(?:^|\n)Quesito\s+(\d+)',  # Quesito 1
        r'(?:^|\n)(?:Ex|Es)\.?\s*(\d+(?:\.\d+)?)',  # Ex. 1, Es 1.2
    ]

    # Secondary patterns - only use if no primary patterns found
    # These often match sub-questions or instructions
    SECONDARY_PATTERNS = [
        r'(?:^|\n)(\d+)\.\s+',  # 1. , 2. , etc.
        r'(?:^|\n)(\d+)\)',  # 1), 2), etc.
    ]

    # Instruction blacklist - patterns that indicate instructions, not exercises
    INSTRUCTION_PATTERNS = [
        r'soluzioni?\s+E\s+procedimenti',  # "soluzioni E procedimenti"
        r'non\s+si\s+può\s+usare',  # "NON si può usare"
        r'nome\s*,\s*cognome\s+e\s+matricola',  # "nome, cognome e matricola"
        r'fogli\s+forniti',  # "fogli forniti"
        r'scritti\s+A\s+PENNA',  # "scritti A PENNA"
        r'without\s+procedure',  # English instructions
        r'is\s+not\s+allowed',  # English instructions
    ]

    def __init__(self):
        """Initialize exercise splitter."""
        self.primary_patterns = [re.compile(p, re.MULTILINE | re.IGNORECASE)
                                for p in self.PRIMARY_EXERCISE_PATTERNS]
        self.secondary_patterns = [re.compile(p, re.MULTILINE | re.IGNORECASE)
                                  for p in self.SECONDARY_PATTERNS]
        self.instruction_patterns = [re.compile(p, re.MULTILINE | re.IGNORECASE)
                                    for p in self.INSTRUCTION_PATTERNS]
        self.exercise_counter = 0

    def split_pdf_content(self, pdf_content: PDFContent, course_code: str) -> List[Exercise]:
        """Split PDF content into individual exercises.

        Args:
            pdf_content: Extracted PDF content
            course_code: Course code for ID generation

        Returns:
            List of extracted exercises
        """
        exercises = []
        self.exercise_counter = 0  # Reset counter for each PDF

        # Process each page
        for page in pdf_content.pages:
            page_exercises = self._split_page(page, pdf_content.file_path.name, course_code)
            exercises.extend(page_exercises)

        return exercises

    def _split_page(self, page: PDFPage, source_pdf: str, course_code: str) -> List[Exercise]:
        """Split a single page into exercises.

        Args:
            page: PDF page content
            source_pdf: Source PDF filename
            course_code: Course code

        Returns:
            List of exercises from this page
        """
        text = page.text
        if not text.strip():
            return []

        # Find all exercise markers FIRST
        markers = self._find_exercise_markers(text)

        if not markers:
            # No markers found - check if this is just an instruction page
            if self._is_instruction_page(text):
                return []  # Skip instruction-only pages

            # Not instructions, but no markers either
            # Treat entire page as single exercise if it has substantial content
            # Use a lower threshold to support short exercises (like math problems)
            if len(text.strip()) < 50:  # Too short to be a real exercise
                return []

            return [self._create_exercise(
                text=text,
                page_number=page.page_number,
                exercise_number=None,
                images=page.images,
                has_latex=page.has_latex,
                latex_content=page.latex_content,
                source_pdf=source_pdf,
                course_code=course_code
            )]

        # Split text at markers
        exercises = []
        for i, (start_pos, ex_number) in enumerate(markers):
            # Find end position (start of next exercise or end of text)
            if i + 1 < len(markers):
                end_pos = markers[i + 1][0]
            else:
                end_pos = len(text)

            exercise_text = text[start_pos:end_pos].strip()

            if exercise_text:
                # For now, assign all images from the page to each exercise
                # In a more sophisticated version, we could detect which images
                # belong to which exercise based on position
                exercises.append(self._create_exercise(
                    text=exercise_text,
                    page_number=page.page_number,
                    exercise_number=ex_number,
                    images=page.images if page.images else [],
                    has_latex=page.has_latex,
                    latex_content=page.latex_content,
                    source_pdf=source_pdf,
                    course_code=course_code
                ))

        return exercises

    def _find_exercise_markers(self, text: str) -> List[Tuple[int, str]]:
        """Find all exercise markers in text.

        Strategy:
        1. First try primary patterns (Esercizio, Exercise, etc.)
        2. If primary patterns found, use only those (ignore sub-questions)
        3. If no primary patterns, check for instruction blacklist
        4. Only use secondary patterns if no primary and not instructions

        Args:
            text: Text to search

        Returns:
            List of tuples (position, exercise_number)
        """
        markers = []

        # Try primary patterns first
        for pattern in self.primary_patterns:
            for match in pattern.finditer(text):
                position = match.start()
                ex_number = match.group(1) if match.groups() else None
                markers.append((position, ex_number))

        # If primary patterns found, use only those
        if markers:
            markers = list(set(markers))
            markers.sort(key=lambda x: x[0])
            return markers

        # Check if this looks like instructions
        is_instructions = any(pattern.search(text) for pattern in self.instruction_patterns)
        if is_instructions:
            # Don't split instruction pages
            return []

        # Only use secondary patterns if no primary patterns and not instructions
        # Also require reasonable spacing between markers to avoid over-splitting
        for pattern in self.secondary_patterns:
            for match in pattern.finditer(text):
                position = match.start()
                ex_number = match.group(1) if match.groups() else None

                # Get context around match to filter out false positives
                context_start = max(0, position - 50)
                context_end = min(len(text), position + 150)
                context = text[context_start:context_end]

                # Skip if this looks like an instruction
                if any(p.search(context) for p in self.instruction_patterns):
                    continue

                # Skip very short fragments (likely list items, not exercises)
                # Look ahead to next marker
                next_marker_pos = len(text)
                for other_match in pattern.finditer(text[position+1:]):
                    next_marker_pos = position + 1 + other_match.start()
                    break

                fragment_length = next_marker_pos - position
                if fragment_length < 100:  # Minimum 100 chars for an exercise
                    continue

                markers.append((position, ex_number))

        # Remove duplicates and sort by position
        markers = list(set(markers))
        markers.sort(key=lambda x: x[0])

        return markers

    def _is_instruction_page(self, text: str) -> bool:
        """Check if a page contains only instructions (not exercises).

        Args:
            text: Page text

        Returns:
            True if this is an instruction-only page
        """
        # Check for instruction-only patterns
        instruction_indicators = [
            r'NOME.*COGNOME.*MATRICOLA',  # Header with name fields
            r'Si\s+ricorda\s+che',  # "Si ricorda che" (It is reminded that)
        ]

        # Count how many instruction patterns match
        matches = sum(1 for pattern in self.instruction_patterns +
                     [re.compile(p, re.IGNORECASE) for p in instruction_indicators]
                     if pattern.search(text))

        # If page is mostly instructions and no exercise markers, it's an instruction page
        if matches >= 3:  # At least 3 instruction patterns
            return True

        # Also check if page is very short and contains instructions
        if len(text.strip()) < 500 and matches >= 2:
            return True

        return False

    def _create_exercise(self, text: str, page_number: int,
                        exercise_number: Optional[str],
                        images: List[bytes], has_latex: bool,
                        latex_content: Optional[str], source_pdf: str,
                        course_code: str) -> Exercise:
        """Create an Exercise object.

        Args:
            text: Exercise text
            page_number: Page number
            exercise_number: Exercise number (if detected)
            images: Image data
            has_latex: Whether LaTeX was detected
            latex_content: LaTeX content
            source_pdf: Source PDF filename
            course_code: Course code

        Returns:
            Exercise object
        """
        # Generate unique ID
        exercise_id = self._generate_exercise_id(
            course_code, source_pdf, page_number, exercise_number
        )

        return Exercise(
            id=exercise_id,
            text=text,
            page_number=page_number,
            exercise_number=exercise_number,
            has_images=len(images) > 0,
            image_data=images,
            has_latex=has_latex,
            latex_content=latex_content,
            source_pdf=source_pdf
        )

    def _generate_exercise_id(self, course_code: str, source_pdf: str,
                             page_number: int, exercise_number: Optional[str]) -> str:
        """Generate a unique exercise ID.

        Args:
            course_code: Course code
            source_pdf: Source PDF filename
            page_number: Page number
            exercise_number: Exercise number

        Returns:
            Unique exercise ID
        """
        # Increment counter to ensure uniqueness
        self.exercise_counter += 1

        # Create a hash from ALL components including counter for guaranteed uniqueness
        components = f"{course_code}_{source_pdf}_{page_number}_{exercise_number or 'none'}_{self.exercise_counter}"

        # Generate hash
        hash_obj = hashlib.md5(components.encode())
        short_hash = hash_obj.hexdigest()[:12]

        # Create ID: course abbreviation + counter + hash
        course_abbrev = course_code.lower().replace('b', '').replace('0', '')[:6]
        return f"{course_abbrev}_{self.exercise_counter:04d}_{short_hash}"

    def merge_split_exercises(self, exercises: List[Exercise]) -> List[Exercise]:
        """Merge exercises that were incorrectly split.

        This is a placeholder for future enhancement where we might
        use AI to detect when an exercise was split across pages.

        Args:
            exercises: List of exercises

        Returns:
            Merged list of exercises
        """
        # For now, just return as-is
        # In Phase 3, we could use LLM to detect split exercises
        return exercises

    def validate_exercise(self, exercise: Exercise, min_length: int = 20) -> bool:
        """Validate if an exercise has sufficient content.

        Args:
            exercise: Exercise to validate
            min_length: Minimum text length

        Returns:
            True if exercise is valid
        """
        # Check minimum text length
        if len(exercise.text.strip()) < min_length:
            return False

        # Check if it's not just a header
        if len(exercise.text.split()) < 5:
            return False

        return True

    def clean_exercise_text(self, text: str) -> str:
        """Clean up exercise text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Remove page numbers (common pattern)
        text = re.sub(r'(?:^|\n)Pagina\s+\d+(?:\n|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(?:^|\n)Page\s+\d+(?:\n|$)', '', text, flags=re.IGNORECASE)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text
