# Batch Processing Optimization

## Overview

This document describes the batch processing optimization implemented in Examina to significantly improve exercise analysis performance through parallel API calls.

## Problem Statement

The original implementation analyzed exercises sequentially, making one API call at a time. This approach had significant performance issues:

- **High latency overhead**: Each API call had ~500ms network latency
- **Sequential bottleneck**: With 27 exercises, total time was ~15-20 seconds
- **Inefficient resource usage**: CPU and network idle while waiting for responses
- **Poor user experience**: Long waits for analysis to complete

## Solution: Parallel Batch Processing

### Approach Chosen

We implemented **parallel batch processing using ThreadPoolExecutor** rather than batching multiple exercises in a single API prompt.

**Why parallel API calls over batch prompting?**

1. **Better error isolation**: One failed exercise doesn't affect others
2. **Easier retry logic**: Can retry individual failed exercises
3. **Rate limit management**: Can control concurrency precisely
4. **Maintains merge context**: Each exercise still gets previous exercise context
5. **More flexible**: Can adjust batch size based on provider limits

### Implementation Details

#### Core Components

1. **`merge_exercises_parallel()` method** (`core/analyzer.py`)
   - Processes exercises in parallel batches
   - Uses ThreadPoolExecutor for concurrent API calls
   - Maintains sequential merge logic for fragment detection

2. **`_analyze_exercise_with_retry()` method**
   - Wraps API calls with retry logic
   - Exponential backoff on failures
   - Prevents cascade failures

3. **Configuration** (`config.py`)
   - `Config.BATCH_SIZE = 10`: Default batch size
   - Configurable via `EXAMINA_BATCH_SIZE` environment variable
   - Can be overridden with `--batch-size` CLI flag

4. **CLI Options** (`cli.py`)
   - `--parallel` (default): Use parallel processing
   - `--sequential`: Fallback to original sequential processing
   - `--batch-size <N>`: Override default batch size

## Performance Results

### Benchmark Results (27 exercises, simulated 500ms API latency)

```
Sequential Processing:
  Time: 15.91s
  Rate: 1.70 exercises/second

Parallel Processing (batch_size=10):
  Time: 2.05s
  Rate: 13.18 exercises/second

Performance Improvement:
  Speedup: 7.76x
  Time Saved: 13.86s (87.1% reduction)
  Efficiency: 77.6% of theoretical maximum
```

### Real-World Expectations

With actual API providers (Groq, Anthropic):

- **Expected speedup**: 5-8x
- **For 27 exercises**: ~3-4 seconds vs ~20 seconds
- **For 100 exercises**: ~12-15 seconds vs ~2 minutes
- **For larger courses**: Even more dramatic improvements

## Usage

### Default Behavior (Parallel Processing)

```bash
# Parallel processing is now the default
examina analyze --course ADE --provider groq
```

### Customizing Batch Size

```bash
# Use larger batches for better throughput (if provider allows)
examina analyze --course ADE --batch-size 15

# Use smaller batches to avoid rate limits
examina analyze --course ADE --batch-size 5
```

### Fallback to Sequential

```bash
# Use sequential processing for debugging or small datasets
examina analyze --course ADE --sequential
```

## Technical Trade-offs

### Advantages

✓ **7-8x faster** for typical course sizes
✓ **Better error handling** - isolated failures
✓ **Progress tracking** - real-time batch progress
✓ **Rate limit safe** - controllable concurrency
✓ **Backward compatible** - can still use sequential mode

### Limitations

⚠ **Memory usage**: Slightly higher (stores all analysis results in memory)
⚠ **Rate limits**: Large batches may trigger provider rate limits
⚠ **Complexity**: More complex code than simple sequential loop
⚠ **Thread safety**: Requires careful handling of shared state

### Optimal Batch Sizes by Provider

| Provider   | Recommended Batch Size | Rate Limit |
|------------|------------------------|------------|
| Groq       | 10-15                  | 30 req/min (free tier) |
| Anthropic  | 10-15                  | Varies by tier |
| Ollama     | 5-10                   | Local (no limit) |

## Error Handling

The implementation includes robust error handling:

1. **Retry logic**: Up to 2 retries per exercise with exponential backoff
2. **Graceful degradation**: Failed exercises return default analysis
3. **Batch isolation**: One failed batch doesn't stop the entire process
4. **Progress preservation**: Can resume from checkpoint if interrupted

## Future Improvements

Potential enhancements for future iterations:

1. **Adaptive batch sizing**: Automatically adjust based on rate limit errors
2. **Async/await**: Use asyncio instead of threads for better scalability
3. **Request queuing**: Smart queue management for optimal throughput
4. **Caching**: Cache analysis results to avoid re-analyzing
5. **Distributed processing**: Scale across multiple API keys/accounts

## Migration Guide

### For Users

No action required - parallel processing is now the default. If you experience issues:

1. Try reducing batch size: `--batch-size 5`
2. Fallback to sequential: `--sequential`
3. Check rate limits for your provider

### For Developers

If extending the analyzer:

```python
# Old way (still supported)
merged = analyzer.merge_exercises(exercises)

# New way (recommended)
merged = analyzer.merge_exercises_parallel(
    exercises,
    batch_size=10,
    show_progress=True
)

# Or use the unified method
result = analyzer.discover_topics_and_core_loops(
    course_code,
    batch_size=10,
    use_parallel=True  # or False for sequential
)
```

## Testing

Run the benchmark to verify performance:

```bash
# Run performance benchmark
python3 benchmark_batch.py

# Test with real API (requires API key)
python3 test_batch_performance.py <course_code> <batch_size>
```

## Conclusion

The parallel batch processing optimization provides a **7-8x speedup** for typical exercise analysis tasks, reducing processing time from minutes to seconds. This significantly improves the user experience while maintaining robust error handling and backward compatibility.

For most users, the default settings (`--parallel`, `batch_size=10`) will provide optimal performance. Advanced users can fine-tune batch size based on their provider's rate limits and course size.

---

**Implementation Date**: 2025-11-23
**Version**: 1.0
**Author**: Claude (Anthropic)
