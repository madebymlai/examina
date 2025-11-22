#!/usr/bin/env python3
"""Debug script to analyze splitter behavior."""

import re
from pathlib import Path
from core.pdf_processor import PDFProcessor
from core.exercise_splitter import ExerciseSplitter

def analyze_pdf_splitting(pdf_path: Path):
    """Analyze how a PDF would be split."""

    # Process PDF
    processor = PDFProcessor()
    content = processor.process_pdf(pdf_path)

    print(f"\n{'='*80}")
    print(f"PDF: {pdf_path.name}")
    print(f"Pages: {len(content.pages)}")
    print('='*80)

    # Patterns from ExerciseSplitter
    patterns = [
        (r'(?:^|\n)(?:Esercizio|Exercise|Problema|Problem)\s+(\d+(?:\.\d+)?)', 'Esercizio/Exercise'),
        (r'(?:^|\n)(\d+)\.\s+', 'Numbered (1.)'),
        (r'(?:^|\n)(\d+)\)', 'Numbered (1))'),
        (r'(?:^|\n)Domanda\s+(\d+)', 'Domanda'),
        (r'(?:^|\n)Quesito\s+(\d+)', 'Quesito'),
        (r'(?:^|\n)(?:Ex|Es)\.?\s*(\d+(?:\.\d+)?)', 'Ex/Es'),
    ]

    compiled_patterns = [(re.compile(p, re.MULTILINE | re.IGNORECASE), name)
                        for p, name in patterns]

    # Analyze each page
    for page in content.pages[:5]:  # First 5 pages
        text = page.text
        print(f"\n--- Page {page.page_number} ---")
        print(f"Text length: {len(text)} chars")

        # Find matches for each pattern
        all_markers = []
        for pattern, name in compiled_patterns:
            matches = list(pattern.finditer(text))
            if matches:
                print(f"\n{name} pattern found {len(matches)} matches:")
                for match in matches[:10]:  # First 10 matches
                    start = match.start()
                    # Get context around match
                    context_start = max(0, start - 30)
                    context_end = min(len(text), start + 100)
                    context = text[context_start:context_end].replace('\n', '↵')
                    print(f"  Pos {start}: ...{context}...")
                    all_markers.append((start, match.group(1), name))

        # Show how page would be split (using actual splitter logic)
        splitter = ExerciseSplitter()
        markers = splitter._find_exercise_markers(text)

        print(f"\n==> Page would be split into {len(markers) if markers else 1} fragments (using ACTUAL splitter logic)")
        if markers and len(markers) <= 10:
            print("Split points:")
            for pos, num in markers:
                snippet = text[pos:min(len(text), pos+60)].replace('\n', '↵')
                print(f"  [{num}] at {pos}: {snippet}...")

if __name__ == "__main__":
    # Test on ADE PDFs
    ade_path = Path("data/files/pdfs/B006802/ADE-ESAMI")

    # Test on exam vs notes
    test_files = [
        "Appunti-AE-1-semestre.pdf",  # Lecture notes
        "Compito 2018-01-25 - TESTO.pdf",  # Exam
        "Compito - Prima Prova Intermedia 10-02-2020 - Soluzioni.pdf",  # Solutions
    ]

    for filename in test_files:
        pdf_path = ade_path / filename
        if pdf_path.exists():
            analyze_pdf_splitting(pdf_path)
        else:
            print(f"File not found: {pdf_path}")
