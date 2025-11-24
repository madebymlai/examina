#!/usr/bin/env python3
"""
Debug solution separator to see why confidence is 0.0
"""

from storage.database import Database
from core.solution_separator import SolutionSeparator
from models.llm_manager import LLMManager
import json

print("=" * 60)
print("Debugging Solution Separator")
print("=" * 60)

# Initialize
llm = LLMManager(provider="anthropic")
separator = SolutionSeparator(llm_manager=llm)

# Get one exercise from SO course
with Database() as db:
    cursor = db.conn.execute('''
        SELECT id, text, source_pdf
        FROM exercises
        WHERE course_code = 'B006818'
        AND source_pdf LIKE '%domandeOraleSO%'
        LIMIT 1
    ''')

    row = cursor.fetchone()
    if not row:
        print("No exercises found!")
        exit(1)

    ex_id, text, source = row
    print(f"\nExercise ID: {ex_id}")
    print(f"Source: {source}")
    print(f"Text length: {len(text)} chars")
    print(f"\nFirst 400 chars:\n{text[:400]}\n")

# Step 1: Check if has solution
print("\n[STEP 1] Detecting if text has solution...")
has_sol = separator.has_solution(text)
print(f"Result: {has_sol}")

if not has_sol:
    print("Stopping - no solution detected")
    exit(0)

# Step 2: Separate with debug output
print("\n[STEP 2] Separating with debug output...")

# Manually run the LLM call to see response
prompt = f"""Separate this exercise text into QUESTION and ANSWER parts.

TEXT:
{text}

Task: Identify where the question ends and the answer/solution begins.

Respond in JSON format:
{{
  "question": "the question text only",
  "answer": "the answer/solution text only",
  "confidence": 0.95
}}

Guidelines:
- Question: The problem statement, what's being asked
- Answer: Explanations, definitions, step-by-step solution, reasoning
- Confidence: 0.0-1.0, how clear the boundary is
- If uncertain, err on the side of including more in the question
- Preserve all original text (don't summarize)
"""

response = llm.generate(
    prompt=prompt,
    system="You are an expert at analyzing educational content. Be precise and preserve all original text.",
    temperature=0.0,
    max_tokens=4000,
    json_mode=True
)

print(f"\n[DEBUG] LLM Response Success: {response.success}")
print(f"[DEBUG] Response length: {len(response.text)} chars")
print(f"[DEBUG] First 500 chars of response:\n{response.text[:500]}\n")

if not response.success:
    print("LLM call failed!")
    exit(1)

# Try to parse JSON
try:
    result = json.loads(response.text)
    print(f"[DEBUG] JSON parsing: SUCCESS")
    print(f"[DEBUG] Keys in result: {list(result.keys())}")

    question = result.get('question', '').strip()
    answer = result.get('answer', '').strip()
    confidence = float(result.get('confidence', 0.5))

    print(f"\n[DEBUG] Question length: {len(question)} chars")
    print(f"[DEBUG] Answer length: {len(answer)} chars")
    print(f"[DEBUG] Confidence: {confidence}")

    # Calculate coverage
    combined_length = len(question) + len(answer)
    original_length = len(text)
    coverage_ratio = combined_length / original_length if original_length > 0 else 0

    print(f"\n[DEBUG] Coverage calculation:")
    print(f"  Original length: {original_length}")
    print(f"  Combined length: {combined_length}")
    print(f"  Coverage ratio: {coverage_ratio:.2f}")
    print(f"  Threshold: 0.70")
    print(f"  Passes validation: {coverage_ratio >= 0.7}")

    if coverage_ratio < 0.7:
        print("\n[FAIL] Coverage ratio too low - would return None")
        print(f"\nQuestion preview (first 300 chars):\n{question[:300]}")
        print(f"\nAnswer preview (first 300 chars):\n{answer[:300]}")
    else:
        print("\n[SUCCESS] Would successfully separate!")
        print(f"\nQuestion (first 400 chars):\n{question[:400]}")
        print(f"\nAnswer (first 400 chars):\n{answer[:400]}")

except json.JSONDecodeError as e:
    print(f"[DEBUG] JSON parsing: FAILED")
    print(f"[DEBUG] Error: {e}")
    print(f"[DEBUG] Raw response:\n{response.text}")
except Exception as e:
    print(f"[DEBUG] Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug Complete")
print("=" * 60)
