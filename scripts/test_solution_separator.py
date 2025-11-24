#!/usr/bin/env python3
"""
Quick test of solution separator on 1-2 exercises.
This avoids processing all 87 exercises which takes too long.
"""

from storage.database import Database
from core.solution_separator import SolutionSeparator
from models.llm_manager import LLMManager

print("=" * 60)
print("Testing Solution Separator")
print("=" * 60)

# Initialize
llm = LLMManager(provider="anthropic")
separator = SolutionSeparator(llm_manager=llm)

# Get 2 exercises from SO course
with Database() as db:
    cursor = db.conn.execute('''
        SELECT id, text, source_pdf
        FROM exercises
        WHERE course_code = 'SO'
        LIMIT 2
    ''')

    exercises = cursor.fetchall()
    print(f"\nFound {len(exercises)} exercises to test\n")

    for idx, (ex_id, text, source) in enumerate(exercises, 1):
        print(f"\n{'='*60}")
        print(f"TEST {idx}/{len(exercises)}")
        print(f"{'='*60}")
        print(f"Exercise ID: {ex_id}")
        print(f"Source: {source}")
        print(f"Original length: {len(text)} chars")

        # Step 1: Check if has solution
        print("\n[1] Detecting if text contains solution...")
        has_sol = separator.has_solution(text)
        print(f"    Result: {'YES - has Q+A' if has_sol else 'NO - question only'}")

        if has_sol:
            # Step 2: Separate
            print("\n[2] Separating question from answer...")
            result = separator.separate(text)

            print(f"    Confidence: {result.confidence:.2f}")
            print(f"    Method: {result.separation_method}")

            if result.answer:
                print(f"\n[3] Results:")
                print(f"    Question length: {len(result.question)} chars")
                print(f"    Answer length: {len(result.answer)} chars")
                print(f"    Coverage: {(len(result.question) + len(result.answer)) / len(text) * 100:.1f}%")

                print(f"\n    === QUESTION (first 400 chars) ===")
                print(f"    {result.question[:400]}")
                if len(result.question) > 400:
                    print(f"    ... ({len(result.question) - 400} more chars)")

                print(f"\n    === ANSWER (first 400 chars) ===")
                print(f"    {result.answer[:400]}")
                if len(result.answer) > 400:
                    print(f"    ... ({len(result.answer) - 400} more chars)")
            else:
                print("\n[3] No answer extracted (confidence too low)")
        else:
            print("\n[2] Skipping separation (no solution detected)")

print(f"\n{'='*60}")
print("Test Complete!")
print(f"{'='*60}\n")
