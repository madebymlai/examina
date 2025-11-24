# Resume Capability Implementation

## Overview
This document describes the resume capability feature that allows interrupted or failed exercise analysis to resume from the last checkpoint, saving time and API costs.

## Problem Solved
Previously, if analysis failed midway due to:
- API errors or rate limits
- Network interruptions
- User interruption (Ctrl+C)
- System crashes

Users had to restart the entire analysis from scratch, wasting:
- Time (re-analyzing already processed exercises)
- Money (redundant API calls)
- Frustration (losing progress)

## Solution: Checkpoint-Based Resume

### How It Works

1. **Database Tracking**: Each exercise has an `analyzed` flag (boolean) in the database
   - `analyzed = 0`: Exercise not yet analyzed
   - `analyzed = 1`: Exercise successfully analyzed

2. **Progress Detection**: When starting analysis, the system:
   - Counts total exercises for the course
   - Counts already-analyzed exercises
   - Counts remaining unanalyzed exercises
   - Shows progress summary to user

3. **Resume Logic**:
   - If some exercises are already analyzed → Resume from checkpoint
   - If all exercises are analyzed → Skip analysis (suggest --force)
   - If none are analyzed → Start fresh

4. **Skip Mechanism**: During analysis, already-analyzed exercises are skipped
   - Preserves existing topic/core_loop assignments
   - Doesn't re-run LLM analysis
   - Maintains deduplication mappings

### Files Modified

#### 1. `/home/laimk/git/Examina/storage/database.py`
**Changes:**
- Modified `get_exercises_by_course()` to accept filtering parameters:
  - `analyzed_only=True`: Return only analyzed exercises
  - `unanalyzed_only=True`: Return only unanalyzed exercises

**Example:**
```python
# Get all exercises (default behavior)
all_exercises = db.get_exercises_by_course('B006802')

# Get only analyzed exercises
analyzed = db.get_exercises_by_course('B006802', analyzed_only=True)

# Get only unanalyzed exercises
remaining = db.get_exercises_by_course('B006802', unanalyzed_only=True)
```

#### 2. `/home/laimk/git/Examina/core/analyzer.py`
**Changes:**
- Modified `merge_exercises()` to accept `skip_analyzed` parameter
  - When True, skips exercises where `analyzed = 1`
  - Saves current merge before skipping to avoid state corruption

- Modified `discover_topics_and_core_loops()` to accept `skip_analyzed` parameter
  - Passes parameter down to `merge_exercises()`
  - Returns accurate counts for progress tracking

**Example:**
```python
# Resume mode: skip already analyzed
merged = analyzer.merge_exercises(exercises, skip_analyzed=True)

# Force mode: analyze everything
merged = analyzer.merge_exercises(exercises, skip_analyzed=False)
```

#### 3. `/home/laimk/git/Examina/cli.py`
**Changes:**

1. **Added --force flag:**
   ```python
   @click.option('--force', '-f', is_flag=True,
                 help='Force re-analysis of all exercises (ignore existing analysis)')
   ```

2. **Progress Detection (lines 342-358):**
   ```python
   # Get exercise counts
   all_exercises = db.get_exercises_by_course(course_code)
   analyzed_exercises = db.get_exercises_by_course(course_code, analyzed_only=True)
   unanalyzed_exercises = db.get_exercises_by_course(course_code, unanalyzed_only=True)

   # Display progress
   console.print(f"Found {total_count} exercise fragments")
   console.print(f"  Already analyzed: {analyzed_count}")
   console.print(f"  Remaining: {remaining_count}")
   ```

3. **Resume Logic (lines 360-373):**
   ```python
   if force:
       # Re-analyze everything
       console.print("--force flag: Re-analyzing all exercises")
       db.conn.execute("UPDATE exercises SET analyzed = 0 WHERE course_code = ?",
                      (course_code,))
   elif remaining_count == 0:
       # All done
       console.print("All exercises already analyzed! Use --force to re-analyze.")
       return
   else:
       # Resume
       if analyzed_count > 0:
           console.print(f"Resuming analysis from checkpoint ({remaining_count} remaining)...")
   ```

4. **Skip Analyzed Flag (line 423):**
   ```python
   skip_analyzed = not force and analyzed_count > 0

   discovery_result = analyzer.discover_topics_and_core_loops(
       course_code,
       skip_analyzed=skip_analyzed
   )
   ```

5. **Progress Display (lines 420-425):**
   ```python
   if skip_analyzed:
       newly_analyzed = discovery_result['merged_count']
       console.print(f"✓ Analyzed {newly_analyzed} new exercises (skipped {analyzed_count} already analyzed)")
       console.print(f"  Total progress: {analyzed_count + newly_analyzed}/{total_count} exercises")
   ```

## Usage Examples

### Scenario 1: First Analysis (No Previous Progress)
```bash
$ examina analyze --course ADE --provider groq

Analyzing exercises for ADE...
Course: Computer Architecture (ADE)

Found 27 exercise fragments
  Already analyzed: 0
  Remaining: 27

🤖 Initializing AI components...
🔍 Analyzing and merging exercise fragments...
```

### Scenario 2: Interrupted Analysis (Resume)
```bash
# After first run analyzed 10/27, then got interrupted...

$ examina analyze --course ADE --provider groq

Analyzing exercises for ADE...
Course: Computer Architecture (ADE)

Found 27 exercise fragments
  Already analyzed: 10
  Remaining: 17

Resuming analysis from checkpoint (17 exercises remaining)...

🤖 Initializing AI components...
🔍 Analyzing and merging exercise fragments...
✓ Analyzed 17 new exercises (skipped 10 already analyzed)
  Total progress: 27/27 exercises
```

### Scenario 3: Already Complete
```bash
$ examina analyze --course ADE --provider groq

Analyzing exercises for ADE...
Course: Computer Architecture (ADE)

Found 27 exercise fragments
  Already analyzed: 27
  Remaining: 0

All exercises already analyzed! Use --force to re-analyze.
```

### Scenario 4: Force Re-analysis
```bash
$ examina analyze --course ADE --provider groq --force

Analyzing exercises for ADE...
Course: Computer Architecture (ADE)

Found 27 exercise fragments
  Already analyzed: 27
  Remaining: 0

--force flag: Re-analyzing all exercises

🤖 Initializing AI components...
🔍 Analyzing and merging exercise fragments...
✓ Merged 27 fragments → 12 exercises
```

## What --force Flag Does

The `--force` flag:

1. **Resets Progress**: Sets `analyzed = 0` for all exercises in the course
2. **Re-runs Analysis**: Analyzes all exercises from scratch
3. **Overwrites Results**: Replaces existing topic/core_loop assignments
4. **Updates Vector Store**: Rebuilds embeddings for the course

**When to use --force:**
- Algorithm/prompt improvements that warrant re-analysis
- Fixing errors in previous analysis
- Changing output language (--lang parameter)
- Testing different analysis parameters

**Warning:** Using --force costs API credits and time. Only use when necessary.

## Deduplication & Resume

**Important:** Deduplication still works correctly with resumed analysis because:

1. Each analysis run performs its own deduplication
2. Topic/core loop similarity detection runs on the full result set
3. Previously analyzed exercises contribute to the deduplicated mapping
4. New exercises are merged into existing deduplicated topics/loops

## Testing Resume Capability

Use the included test script:

```bash
$ python test_resume.py

=== Exercise Analysis Status ===

B006802:
  Total: 27
  Analyzed: 27
  Remaining: 0
  Progress: 27/27 (100%)

B006807:
  Total: 38
  Analyzed: 4
  Remaining: 34
  Progress: 4/38 (10%)
```

## Implementation Notes

### Database Schema
The `analyzed` flag was already present in the schema:
```sql
CREATE TABLE exercises (
    ...
    analyzed BOOLEAN DEFAULT 0,
    ...
)
```

### Checkpoint Granularity
- Checkpoints occur at the **exercise** level (not sub-fragment level)
- When an exercise is successfully analyzed, `analyzed = 1` is written to DB
- This provides fine-grained resume capability

### Edge Cases Handled

1. **Partial Merge Groups**: If analysis stops mid-merge, the next run will properly handle fragment merging
2. **Low Confidence Exercises**: Skipped exercises are still marked as analyzed (`low_confidence_skipped = 1`)
3. **Force Mode After Partial Progress**: Correctly resets and re-analyzes everything
4. **Empty Remaining**: Gracefully exits with helpful message

## Performance Impact

Resume capability adds **minimal overhead**:
- Database queries: +2 SELECT queries at startup (negligible)
- Skip logic: O(n) iteration with early continue (very fast)
- Memory: Same as before (loads all exercises for context)

**Benefits:**
- Saves 100% of API costs for already-analyzed exercises
- Saves 100% of time for already-analyzed exercises
- No data loss on interruption

## Future Improvements

Potential enhancements:
1. Periodic auto-checkpoint during long-running analysis
2. Progress bar showing real-time completion
3. Estimate time remaining based on rate
4. Detailed error logging for failed exercises
5. Selective re-analysis (e.g., only re-analyze low-confidence exercises)

## Conclusion

The resume capability makes Examina's analysis robust and cost-effective. Users can:
- Safely interrupt analysis without losing progress
- Handle API errors gracefully
- Resume from any checkpoint
- Avoid wasting API credits on re-analysis

This is critical for production use where analysis may take hours and API reliability cannot be guaranteed.
