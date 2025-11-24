#!/usr/bin/env python3
"""
Performance test script for batch processing optimization.
Compares sequential vs parallel analysis performance.
"""

import time
import sys
from storage.database import Database
from models.llm_manager import LLMManager
from core.analyzer import ExerciseAnalyzer
from config import Config

def test_performance(course_code: str, batch_size: int = 10):
    """Test and compare sequential vs parallel processing performance."""

    print("=" * 80)
    print("BATCH PROCESSING PERFORMANCE TEST")
    print("=" * 80)
    print()

    # Get exercises
    with Database() as db:
        exercises = db.get_exercises_by_course(course_code)

    if not exercises:
        print(f"Error: No exercises found for course {course_code}")
        return

    print(f"Course: {course_code}")
    print(f"Total exercises: {len(exercises)}")
    print(f"Batch size: {batch_size}")
    print()

    # Initialize components
    print("Initializing LLM manager (Groq API)...")
    llm = LLMManager(provider="groq")
    analyzer = ExerciseAnalyzer(llm, language="en")
    print()

    # Test 1: Sequential Processing
    print("-" * 80)
    print("TEST 1: SEQUENTIAL PROCESSING")
    print("-" * 80)
    print()

    start_time = time.time()
    sequential_result = analyzer.merge_exercises(exercises)
    sequential_time = time.time() - start_time

    print()
    print(f"Sequential processing completed in {sequential_time:.2f}s")
    print(f"  Merged exercises: {len(sequential_result)}")
    print(f"  Rate: {len(exercises)/sequential_time:.2f} exercises/second")
    print()

    # Test 2: Parallel Processing
    print("-" * 80)
    print("TEST 2: PARALLEL PROCESSING")
    print("-" * 80)
    print()

    start_time = time.time()
    parallel_result = analyzer.merge_exercises_parallel(
        exercises,
        batch_size=batch_size,
        show_progress=True
    )
    parallel_time = time.time() - start_time

    print()
    print(f"Parallel processing completed in {parallel_time:.2f}s")
    print(f"  Merged exercises: {len(parallel_result)}")
    print(f"  Rate: {len(exercises)/parallel_time:.2f} exercises/second")
    print()

    # Calculate improvement
    print("=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print()
    print(f"Sequential time:  {sequential_time:.2f}s")
    print(f"Parallel time:    {parallel_time:.2f}s")
    print()

    speedup = sequential_time / parallel_time
    time_saved = sequential_time - parallel_time
    improvement_pct = ((sequential_time - parallel_time) / sequential_time) * 100

    print(f"Speedup:          {speedup:.2f}x")
    print(f"Time saved:       {time_saved:.2f}s ({improvement_pct:.1f}%)")
    print()

    # Validate results are similar
    if len(sequential_result) == len(parallel_result):
        print(f"✓ Result validation: Both methods produced {len(sequential_result)} merged exercises")
    else:
        print(f"⚠ Warning: Different results - Sequential: {len(sequential_result)}, Parallel: {len(parallel_result)}")
    print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    if speedup > 1.5:
        print(f"✓ Parallel processing provides significant speedup ({speedup:.2f}x)")
        print(f"  Recommend using --parallel (default) for all analyses")
    elif speedup > 1.0:
        print(f"✓ Parallel processing provides moderate speedup ({speedup:.2f}x)")
        print(f"  Recommend using --parallel for large datasets")
    else:
        print(f"⚠ Parallel processing slower than sequential ({speedup:.2f}x)")
        print(f"  Consider using --sequential for this dataset size")
    print()

    if batch_size < 5:
        print(f"ℹ Try increasing batch size (--batch-size) for potentially better performance")
    elif batch_size > 20:
        print(f"⚠ Large batch size may hit rate limits - consider reducing to 10-15")
    print()

if __name__ == "__main__":
    # Default to ADE course (B006802)
    course_code = sys.argv[1] if len(sys.argv) > 1 else "B006802"
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else Config.BATCH_SIZE

    test_performance(course_code, batch_size)
