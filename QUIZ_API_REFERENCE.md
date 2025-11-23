# QuizManager API Reference

Quick reference for the QuizManager and SM2Algorithm classes.

## QuizManager

### Initialization

```python
from core.quiz import QuizManager
from models.llm_manager import LLMManager

# Basic initialization
quiz_manager = QuizManager()

# With custom LLM
llm = LLMManager(provider="anthropic")
quiz_manager = QuizManager(llm_manager=llm, language="en")

# With language setting
quiz_manager = QuizManager(language="it")  # Italian
```

### create_quiz()

Create a new quiz session.

```python
session_id = quiz_manager.create_quiz(
    course_code: str,              # Required: Course code (e.g., "B032426")
    quiz_type: str = 'random',     # 'random', 'topic', 'core_loop', 'review'
    question_count: int = 10,      # Number of questions (default: 10)
    topic_id: Optional[int] = None,          # Filter by topic ID
    core_loop_id: Optional[str] = None,      # Filter by core loop ID
    difficulty: Optional[str] = None,        # 'easy', 'medium', 'hard'
    prioritize_due: bool = True    # Prioritize due exercises
) -> str  # Returns: session_id (UUID string)
```

**Quiz Types**:
- `'random'`: Random exercises from course
- `'topic'`: Exercises from specific topic (requires `topic_id`)
- `'core_loop'`: Exercises from specific core loop (requires `core_loop_id`)
- `'review'`: Only exercises due for review (SM-2 based)

**Examples**:

```python
# Random quiz with 10 questions
session_id = quiz_manager.create_quiz("B032426")

# Review quiz (spaced repetition)
session_id = quiz_manager.create_quiz(
    course_code="B032426",
    quiz_type="review",
    question_count=15
)

# Topic-specific quiz
session_id = quiz_manager.create_quiz(
    course_code="B032426",
    quiz_type="topic",
    topic_id=5,
    question_count=8
)

# Medium difficulty only
session_id = quiz_manager.create_quiz(
    course_code="B032426",
    difficulty="medium",
    question_count=12
)
```

### get_next_question()

Get the next unanswered question.

```python
question = quiz_manager.get_next_question(
    session_id: str  # Quiz session ID
) -> Optional[Dict]  # Returns: question dict or None if complete
```

**Returns**:
```python
{
    'question_number': 1,           # Current question number
    'total_questions': 10,          # Total questions in quiz
    'exercise_id': 'ex_abc123',     # Exercise ID
    'text': 'Question text...',     # Question text
    'difficulty': 'medium',         # Difficulty level
    'core_loop_id': 'cl_xyz',       # Core loop ID
    'topic_id': 5,                  # Topic ID
    'has_images': False,            # Whether question has images
    'image_paths': []               # List of image paths
}
```

**Example**:

```python
while True:
    question = quiz_manager.get_next_question(session_id)
    if not question:
        break  # Quiz complete

    print(f"Q{question['question_number']}/{question['total_questions']}")
    print(question['text'])
```

### submit_answer()

Submit an answer and get feedback.

```python
result = quiz_manager.submit_answer(
    session_id: str,        # Quiz session ID
    exercise_id: str,       # Exercise ID (from question)
    user_answer: str,       # User's answer text
    time_taken: int,        # Time in seconds
    hint_used: bool = False # Whether hints were used
) -> Dict  # Returns: result dictionary
```

**Returns**:
```python
{
    'correct': True,                   # Boolean correctness
    'score': 0.95,                     # Score (0.0 to 1.0)
    'feedback': 'AI feedback text...', # AI-generated feedback
    'sm2_update': {                    # SM-2 update data
        'easiness_factor': 2.5,
        'repetition_number': 1,
        'interval_days': 6,
        'next_review': '2025-11-29T...',
        'quality': 5,
        'mastery_score': 0.85
    },
    'remaining_questions': 9           # Questions left
}
```

**Example**:

```python
import time

start_time = time.time()
user_answer = input("Your answer: ")
time_taken = int(time.time() - start_time)

result = quiz_manager.submit_answer(
    session_id=session_id,
    exercise_id=question['exercise_id'],
    user_answer=user_answer,
    time_taken=time_taken,
    hint_used=False
)

print(f"Correct: {result['correct']}")
print(f"Score: {result['score']:.2f}")
print(f"Feedback: {result['feedback']}")
print(f"Next review in {result['sm2_update']['interval_days']} days")
```

### complete_quiz()

Complete quiz and get final statistics.

```python
stats = quiz_manager.complete_quiz(
    session_id: str  # Quiz session ID
) -> Dict  # Returns: statistics dictionary
```

**Returns**:
```python
{
    'completed': True,
    'session_id': 'abc-123-...',
    'total_questions': 10,
    'total_correct': 8,
    'final_score': 85.5,              # Percentage
    'average_score': 0.855,           # 0.0 to 1.0
    'total_time_seconds': 600,
    'difficulty_breakdown': {
        'easy': {
            'total': 3,
            'correct': 3,
            'percentage': 100.0
        },
        'medium': {
            'total': 5,
            'correct': 4,
            'percentage': 80.0
        },
        'hard': {
            'total': 2,
            'correct': 1,
            'percentage': 50.0
        }
    },
    'passed': True                     # 60% threshold
}
```

**Example**:

```python
stats = quiz_manager.complete_quiz(session_id)

print(f"Quiz Complete!")
print(f"Score: {stats['final_score']:.1f}%")
print(f"Correct: {stats['total_correct']}/{stats['total_questions']}")
print(f"Passed: {'Yes' if stats['passed'] else 'No'}")

for difficulty, data in stats['difficulty_breakdown'].items():
    print(f"{difficulty}: {data['correct']}/{data['total']} ({data['percentage']:.1f}%)")
```

### get_quiz_status()

Get current quiz status.

```python
status = quiz_manager.get_quiz_status(
    session_id: str  # Quiz session ID
) -> Dict  # Returns: status dictionary
```

**Returns**:
```python
{
    'session_id': 'abc-123-...',
    'course_code': 'B032426',
    'quiz_type': 'random',
    'total_questions': 10,
    'answered': 5,
    'remaining': 5,
    'started_at': '2025-11-23T...',
    'completed': False,
    'completed_at': None
}
```

**Example**:

```python
status = quiz_manager.get_quiz_status(session_id)
print(f"Progress: {status['answered']}/{status['total_questions']}")
print(f"Remaining: {status['remaining']}")
```

---

## SM2Algorithm

### Initialization

```python
from core.sm2 import SM2Algorithm

sm2 = SM2Algorithm()
```

### calculate()

Calculate next review using SM-2 algorithm.

```python
from datetime import datetime

result = sm2.calculate(
    quality: int,                         # Quality rating (0-5)
    easiness_factor: float = 2.5,         # Current EF (1.3-2.5)
    repetition_number: int = 0,           # Consecutive correct
    previous_interval: int = 0,           # Previous interval (days)
    base_date: Optional[datetime] = None  # Base date (default: now)
) -> SM2Result
```

**Quality Scale**:
- `5`: Perfect (immediate, effortless)
- `4`: Correct with hesitation
- `3`: Correct with difficulty
- `2`: Incorrect; answer seemed easy
- `1`: Incorrect; answer seemed familiar
- `0`: Complete blackout

**Returns** (`SM2Result`):
```python
SM2Result(
    easiness_factor=2.5,        # New EF (1.3-2.5)
    repetition_number=1,        # New repetition count
    interval_days=6,            # Days until next review
    next_review_date=datetime,  # Next review datetime
    quality=5                   # Input quality
)
```

**Examples**:

```python
# First review (perfect recall)
result = sm2.calculate(quality=5)
print(f"Review again in {result.interval_days} days")
# Output: Review again in 1 days

# Second review (perfect recall)
result = sm2.calculate(
    quality=5,
    easiness_factor=2.5,
    repetition_number=1,
    previous_interval=1
)
print(f"Review again in {result.interval_days} days")
# Output: Review again in 6 days

# Third review (perfect recall)
result = sm2.calculate(
    quality=5,
    easiness_factor=2.5,
    repetition_number=2,
    previous_interval=6
)
print(f"Review again in {result.interval_days} days")
# Output: Review again in 15 days (6 × 2.5)

# Failed review (resets)
result = sm2.calculate(quality=1, repetition_number=2)
print(f"Repetition reset to: {result.repetition_number}")
print(f"Review again in {result.interval_days} days")
# Output: Repetition reset to: 0
#         Review again in 1 days
```

### convert_score_to_quality()

Convert quiz score to SM-2 quality rating.

```python
quality = sm2.convert_score_to_quality(
    score: float,                       # Score (0.0 to 1.0)
    hint_used: bool = False,            # Hints used flag
    time_ratio: Optional[float] = None  # Time ratio (optional)
) -> int  # Returns: quality (0-5)
```

**Conversion Table**:
```
Score       Quality
≥ 0.95  →   5 (Perfect)
≥ 0.85  →   4 (Good)
≥ 0.70  →   3 (Passable)
≥ 0.50  →   2 (Difficult)
≥ 0.20  →   1 (Familiar)
<  0.20 →   0 (Failed)
```

**Adjustments**:
- Hint used: Reduce quality by 1 (if > 0)
- Time > 2x expected: Reduce quality by 1 (if > 0)

**Examples**:

```python
# Perfect score
quality = sm2.convert_score_to_quality(1.0)
# Returns: 5

# Good score
quality = sm2.convert_score_to_quality(0.9)
# Returns: 4

# Good score but used hints
quality = sm2.convert_score_to_quality(0.9, hint_used=True)
# Returns: 3 (reduced by 1)

# Slow but correct
quality = sm2.convert_score_to_quality(0.95, time_ratio=2.5)
# Returns: 4 (reduced by 1 due to slowness)
```

### is_due_for_review()

Check if an item needs review.

```python
from datetime import datetime, timedelta

is_due = sm2.is_due_for_review(
    last_review: datetime,              # Last review date
    interval_days: int,                 # Interval in days
    current_date: Optional[datetime] = None  # Current date
) -> bool  # Returns: True if due
```

**Example**:

```python
from datetime import datetime, timedelta

last_review = datetime.now() - timedelta(days=7)
interval = 6

if sm2.is_due_for_review(last_review, interval):
    print("Item is due for review!")
else:
    print("Not due yet")
# Output: Item is due for review!
```

### get_next_review_date()

Calculate next review date.

```python
from datetime import datetime, timedelta

next_date = sm2.get_next_review_date(
    last_review: datetime,  # Last review date
    interval_days: int      # Interval in days
) -> datetime  # Returns: next review datetime
```

**Example**:

```python
from datetime import datetime

last_review = datetime(2025, 11, 23)
interval = 6

next_review = sm2.get_next_review_date(last_review, interval)
print(f"Next review: {next_review.strftime('%Y-%m-%d')}")
# Output: Next review: 2025-11-29
```

---

## Complete Example: Quiz Session

```python
from core.quiz import QuizManager
import time

# Initialize
quiz_manager = QuizManager(language="en")

# Create quiz
session_id = quiz_manager.create_quiz(
    course_code="B032426",
    quiz_type="review",
    question_count=5,
    prioritize_due=True
)

print(f"Quiz created: {session_id}\n")

# Quiz loop
question_num = 1
while True:
    # Get next question
    question = quiz_manager.get_next_question(session_id)
    if not question:
        print("\nNo more questions!")
        break

    # Display question
    print(f"Question {question_num}/{question['total_questions']}")
    print(f"Difficulty: {question['difficulty']}")
    print(f"\n{question['text']}\n")

    # Get answer (simulated)
    start_time = time.time()
    user_answer = input("Your answer: ")
    time_taken = int(time.time() - start_time)

    # Submit answer
    result = quiz_manager.submit_answer(
        session_id=session_id,
        exercise_id=question['exercise_id'],
        user_answer=user_answer,
        time_taken=time_taken,
        hint_used=False
    )

    # Show feedback
    print(f"\n{'✓' if result['correct'] else '✗'} {result['feedback']}\n")
    print(f"Score: {result['score']:.2f}")
    print(f"Next review: {result['sm2_update']['interval_days']} days")
    print(f"Remaining: {result['remaining_questions']}\n")
    print("-" * 60 + "\n")

    question_num += 1

# Complete quiz
stats = quiz_manager.complete_quiz(session_id)

# Show results
print("\n" + "=" * 60)
print("QUIZ COMPLETE")
print("=" * 60)
print(f"Final Score: {stats['final_score']:.1f}%")
print(f"Correct: {stats['total_correct']}/{stats['total_questions']}")
print(f"Time: {stats['total_time_seconds']}s")
print(f"Result: {'PASSED' if stats['passed'] else 'FAILED'}")

if stats.get('difficulty_breakdown'):
    print("\nBreakdown by Difficulty:")
    for difficulty, data in stats['difficulty_breakdown'].items():
        print(f"  {difficulty.upper()}: {data['correct']}/{data['total']} ({data['percentage']:.1f}%)")
```

---

## Error Handling

### Common Errors

**ValueError: No exercises found**
```python
try:
    session_id = quiz_manager.create_quiz(
        course_code="INVALID",
        quiz_type="random"
    )
except ValueError as e:
    print(f"Error: {e}")
    # Handle: Check filters, course exists, exercises available
```

**Session not found**
```python
status = quiz_manager.get_quiz_status("invalid-session-id")
if 'error' in status:
    print(f"Error: {status['error']}")
    # Handle: Invalid session ID
```

**No more questions**
```python
question = quiz_manager.get_next_question(session_id)
if question is None:
    print("Quiz complete!")
    # Handle: Call complete_quiz()
```

### Best Practices

1. **Always check return values**:
   ```python
   question = quiz_manager.get_next_question(session_id)
   if question:
       # Process question
   ```

2. **Handle API failures gracefully**:
   ```python
   result = quiz_manager.submit_answer(...)
   if not result.get('feedback'):
       print("Evaluation failed, please try again")
   ```

3. **Track time accurately**:
   ```python
   import time
   start = time.time()
   # ... user answers ...
   elapsed = int(time.time() - start)
   ```

4. **Complete quizzes properly**:
   ```python
   while (question := quiz_manager.get_next_question(session_id)):
       # ... answer question ...

   # Always complete when done
   stats = quiz_manager.complete_quiz(session_id)
   ```

---

## Database Schema

### quiz_sessions

```sql
id TEXT PRIMARY KEY              -- Session UUID
course_code TEXT                 -- Course code
quiz_type TEXT                   -- 'random', 'topic', 'core_loop', 'review'
topic_id INTEGER                 -- Optional topic filter
core_loop_id TEXT                -- Optional core loop filter
total_questions INTEGER          -- Total question count
started_at TIMESTAMP             -- Start time
completed_at TIMESTAMP           -- End time (NULL if incomplete)
total_correct INTEGER            -- Correct answers
score REAL                       -- Final score percentage
time_spent INTEGER               -- Total time in seconds
```

### quiz_answers

```sql
id INTEGER PRIMARY KEY           -- Answer ID
session_id TEXT                  -- FK to quiz_sessions
exercise_id TEXT                 -- FK to exercises
question_number INTEGER          -- Question order
student_answer TEXT              -- User's answer
is_correct BOOLEAN               -- Correctness
score REAL                       -- Score (0.0-1.0)
hint_used BOOLEAN                -- Hints used flag
answered_at TIMESTAMP            -- Submission time
time_spent INTEGER               -- Time in seconds
```

### student_progress

```sql
id INTEGER PRIMARY KEY           -- Progress ID
course_code TEXT                 -- Course code
core_loop_id TEXT                -- Core loop ID
total_attempts INTEGER           -- All attempts
correct_attempts INTEGER         -- Correct attempts
mastery_score REAL               -- Percentage correct
last_practiced TIMESTAMP         -- Last practice time
next_review TIMESTAMP            -- Next review time
review_interval INTEGER          -- SM-2 interval (days)
```
