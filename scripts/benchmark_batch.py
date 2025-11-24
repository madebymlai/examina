#!/usr/bin/env python3
"""
Simple benchmark to demonstrate parallel vs sequential batch processing benefits.
This simulates API calls without actually making them.
"""

import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def simulate_api_call(exercise_id: int, delay: float = 0.5):
    """Simulate an API call with random delay."""
    time.sleep(delay + random.uniform(0, 0.2))  # Simulate network latency
    return f"Exercise {exercise_id} analyzed"

def sequential_processing(num_exercises: int, api_delay: float = 0.5):
    """Process exercises sequentially (one at a time)."""
    print(f"Sequential processing {num_exercises} exercises...")
    start = time.time()

    results = []
    for i in range(num_exercises):
        result = simulate_api_call(i, api_delay)
        results.append(result)
        if (i + 1) % 5 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            eta = (num_exercises - i - 1) / rate if rate > 0 else 0
            print(f"  Progress: {i+1}/{num_exercises} | {rate:.2f} ex/s | ETA: {eta:.0f}s")

    elapsed = time.time() - start
    return results, elapsed

def parallel_processing(num_exercises: int, batch_size: int = 10, api_delay: float = 0.5):
    """Process exercises in parallel batches."""
    print(f"Parallel processing {num_exercises} exercises (batch_size={batch_size})...")
    start = time.time()

    results = []
    processed = 0

    for batch_start in range(0, num_exercises, batch_size):
        batch_end = min(batch_start + batch_size, num_exercises)
        batch_indices = list(range(batch_start, batch_end))

        print(f"  Batch {batch_start//batch_size + 1}/{(num_exercises + batch_size - 1)//batch_size} (exercises {batch_start+1}-{batch_end})...")

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {executor.submit(simulate_api_call, idx, api_delay): idx for idx in batch_indices}

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                processed += 1

                if processed % 5 == 0:
                    elapsed = time.time() - start
                    rate = processed / elapsed if elapsed > 0 else 0
                    eta = (num_exercises - processed) / rate if rate > 0 else 0
                    print(f"    Progress: {processed}/{num_exercises} | {rate:.2f} ex/s | ETA: {eta:.0f}s")

    elapsed = time.time() - start
    return results, elapsed

def run_benchmark():
    """Run the benchmark comparing sequential vs parallel processing."""
    print("=" * 80)
    print("BATCH PROCESSING BENCHMARK")
    print("=" * 80)
    print()

    # Configuration
    num_exercises = 27  # ADE course has 27 exercises
    api_delay = 0.5  # Simulate 500ms API call
    batch_size = 10  # Process 10 at a time

    print(f"Configuration:")
    print(f"  Exercises: {num_exercises}")
    print(f"  Simulated API delay: {api_delay}s")
    print(f"  Batch size: {batch_size}")
    print()

    # Test 1: Sequential
    print("-" * 80)
    print("TEST 1: SEQUENTIAL PROCESSING")
    print("-" * 80)
    print()

    seq_results, seq_time = sequential_processing(num_exercises, api_delay)

    print()
    print(f"✓ Sequential completed in {seq_time:.2f}s")
    print(f"  Rate: {num_exercises/seq_time:.2f} exercises/second")
    print()

    # Test 2: Parallel
    print("-" * 80)
    print("TEST 2: PARALLEL BATCH PROCESSING")
    print("-" * 80)
    print()

    par_results, par_time = parallel_processing(num_exercises, batch_size, api_delay)

    print()
    print(f"✓ Parallel completed in {par_time:.2f}s")
    print(f"  Rate: {num_exercises/par_time:.2f} exercises/second")
    print()

    # Comparison
    print("=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print()

    speedup = seq_time / par_time
    time_saved = seq_time - par_time
    improvement_pct = ((seq_time - par_time) / seq_time) * 100

    print(f"Sequential time:  {seq_time:.2f}s")
    print(f"Parallel time:    {par_time:.2f}s")
    print()
    print(f"Speedup:          {speedup:.2f}x")
    print(f"Time saved:       {time_saved:.2f}s ({improvement_pct:.1f}%)")
    print()

    # Analysis
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    theoretical_speedup = min(batch_size, num_exercises)
    efficiency = (speedup / theoretical_speedup) * 100

    print(f"Theoretical max speedup: {theoretical_speedup:.2f}x")
    print(f"Actual speedup:          {speedup:.2f}x")
    print(f"Efficiency:              {efficiency:.1f}%")
    print()

    print("Explanation:")
    print(f"  - Sequential: Each API call waits {api_delay}s → Total: ~{num_exercises * api_delay:.0f}s")
    print(f"  - Parallel:   {batch_size} calls at once → Total: ~{(num_exercises / batch_size) * api_delay:.0f}s")
    print(f"  - Network overhead and batch coordination reduce ideal speedup")
    print()

    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS FOR REAL-WORLD USAGE")
    print("=" * 80)
    print()

    print("Based on this benchmark:")
    print()
    print(f"1. Use --parallel (default) for courses with 10+ exercises")
    print(f"   → Expect {speedup:.1f}x-{speedup*0.8:.1f}x speedup in real scenarios")
    print()
    print(f"2. Optimal batch size: 10-15 exercises")
    print(f"   → Balances parallelism with rate limit safety")
    print()
    print(f"3. For 27 exercises like ADE course:")
    print(f"   → Sequential: ~{seq_time:.0f}s, Parallel: ~{par_time:.0f}s")
    print(f"   → Save {time_saved:.0f}s ({improvement_pct:.0f}%) processing time")
    print()
    print(f"4. Use --sequential only for:")
    print(f"   → Small datasets (< 5 exercises)")
    print(f"   → Debugging individual exercises")
    print(f"   → When hitting rate limits")
    print()

if __name__ == "__main__":
    run_benchmark()
