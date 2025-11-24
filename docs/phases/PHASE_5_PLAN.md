# Phase 5 - Quiz System: Implementation Plan

## Overview

Build an adaptive quiz system with spaced repetition (SM-2 algorithm) for optimal learning and retention. Track progress, mastery levels, and provide analytics to identify weak areas.

---

## Goals

1. **Adaptive Quizzes** - Generate quizzes based on exercises, topics, or core loops
2. **Spaced Repetition** - Use SM-2 algorithm to schedule optimal review times
3. **Progress Tracking** - Store quiz attempts, scores, and performance data
4. **Analytics** - Visualize mastery levels, identify weak areas, suggest what to study next

---

## Architecture

### New Modules

```
core/
├── quiz.py          # Quiz generation and session management
├── sm2.py           # SM-2 spaced repetition algorithm
└── analytics.py     # Progress tracking and analytics

storage/
└── database.py      # Extended with quiz tables
```

---

## Phase 5.1: Database Schema Extensions

### New Tables

#### 1. `quiz_sessions` - Quiz session metadata
```sql
CREATE TABLE quiz_sessions (
    id TEXT PRIMARY KEY,
    course_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_questions INTEGER,
    correct_answers INTEGER,
    score_percentage REAL,
    quiz_type TEXT,  -- 'topic', 'core_loop', 'random', 'review'
    filter_topic_id INTEGER,
    filter_core_loop_id TEXT,
    filter_difficulty TEXT,
    FOREIGN KEY (course_code) REFERENCES courses(code),
    FOREIGN KEY (filter_topic_id) REFERENCES topics(id)
);
```

#### 2. `quiz_attempts` - Individual question attempts
```sql
CREATE TABLE quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    user_answer TEXT,
    correct BOOLEAN,
    time_taken_seconds INTEGER,
    hint_used BOOLEAN DEFAULT 0,
    feedback TEXT,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES quiz_sessions(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);
```

#### 3. `exercise_reviews` - SM-2 spaced repetition data
```sql
CREATE TABLE exercise_reviews (
    exercise_id TEXT PRIMARY KEY,
    course_code TEXT NOT NULL,
    easiness_factor REAL DEFAULT 2.5,  -- SM-2 EF (1.3-2.5)
    repetition_number INTEGER DEFAULT 0,
    interval_days INTEGER DEFAULT 0,
    next_review_date DATE,
    last_reviewed_at TIMESTAMP,
    total_reviews INTEGER DEFAULT 0,
    correct_reviews INTEGER DEFAULT 0,
    mastery_level TEXT DEFAULT 'new',  -- 'new', 'learning', 'reviewing', 'mastered'
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    FOREIGN KEY (course_code) REFERENCES courses(code)
);
```

#### 4. `topic_mastery` - Aggregated mastery per topic
```sql
CREATE TABLE topic_mastery (
    topic_id INTEGER PRIMARY KEY,
    course_code TEXT NOT NULL,
    exercises_total INTEGER DEFAULT 0,
    exercises_mastered INTEGER DEFAULT 0,
    mastery_percentage REAL DEFAULT 0.0,
    last_practiced_at TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id),
    FOREIGN KEY (course_code) REFERENCES courses(code)
);
```

### Migration Strategy
- Add automatic migration in `database.py` `_run_migrations()`
- Check for table existence before creating
- Graceful handling of existing data

**Estimated effort:** 2-3 hours

---

## Phase 5.2: SM-2 Algorithm Implementation

### File: `core/sm2.py`

Implement the SuperMemo 2 (SM-2) spaced repetition algorithm:

```python
class SM2:
    """SuperMemo 2 spaced repetition algorithm."""

    def __init__(self):
        self.MIN_EF = 1.3
        self.MAX_EF = 2.5

    def calculate_next_review(self, quality: int, current_ef: float,
                              current_interval: int, repetition: int) -> dict:
        """
        Calculate next review based on quality of recall.

        Args:
            quality: 0-5 (0=complete blackout, 5=perfect recall)
            current_ef: Current easiness factor (1.3-2.5)
            current_interval: Current interval in days
            repetition: Number of consecutive correct reviews

        Returns:
            dict with: new_ef, new_interval, new_repetition, next_review_date
        """
        # SM-2 algorithm implementation

    def get_review_quality_from_score(self, correct: bool,
                                     time_taken: int,
                                     hint_used: bool) -> int:
        """Convert quiz performance to SM-2 quality (0-5)."""
        # Mapping logic

    def get_due_exercises(self, course_code: str) -> List[str]:
        """Get exercises due for review today."""
        # Query exercise_reviews where next_review_date <= today

    def update_mastery_level(self, exercise_id: str) -> str:
        """Update mastery level based on review history."""
        # 'new' -> 'learning' -> 'reviewing' -> 'mastered'
```

### Key Features
- **Quality scoring** (0-5):
  - 5: Perfect (correct, fast, no hints)
  - 4: Correct (slow or hint used)
  - 3: Correct with difficulty
  - 2: Incorrect but remembered after seeing answer
  - 1: Incorrect, vaguely familiar
  - 0: Complete blackout

- **Interval calculation**:
  - Repetition 0: 1 day
  - Repetition 1: 6 days
  - Repetition 2+: previous_interval × EF

- **Easiness Factor adjustment**:
  - EF' = EF + (0.1 - (5 - quality) × (0.08 + (5 - quality) × 0.02))
  - Clamped between 1.3 and 2.5

- **Mastery levels**:
  - `new`: Never reviewed
  - `learning`: 1-3 reviews, interval < 7 days
  - `reviewing`: 4+ reviews, interval 7-30 days
  - `mastered`: 10+ reviews, interval > 30 days, 90%+ accuracy

**Estimated effort:** 3-4 hours

---

## Phase 5.3: Quiz Session Management

### File: `core/quiz.py`

```python
class QuizManager:
    """Manages quiz sessions and question selection."""

    def create_quiz(self, course_code: str,
                   quiz_type: str = 'random',
                   question_count: int = 10,
                   topic_id: Optional[int] = None,
                   core_loop_id: Optional[str] = None,
                   difficulty: Optional[str] = None,
                   prioritize_due: bool = True) -> str:
        """
        Create a new quiz session.

        Args:
            course_code: Course to quiz on
            quiz_type: 'random', 'topic', 'core_loop', 'review'
            question_count: Number of questions
            topic_id: Filter by topic (if quiz_type='topic')
            core_loop_id: Filter by core loop
            difficulty: Filter by difficulty
            prioritize_due: Prioritize exercises due for review (SM-2)

        Returns:
            session_id
        """

    def get_next_question(self, session_id: str) -> Optional[Dict]:
        """Get next unanswered question in quiz."""

    def submit_answer(self, session_id: str, exercise_id: str,
                     user_answer: str, time_taken: int,
                     hint_used: bool = False) -> Dict:
        """
        Submit answer and get feedback.

        Returns:
            {
                'correct': bool,
                'feedback': str,  # AI-generated feedback
                'sm2_update': dict,  # New SM-2 values
                'remaining_questions': int
            }
        """

    def complete_quiz(self, session_id: str) -> Dict:
        """
        Complete quiz and calculate final score.

        Returns:
            {
                'score_percentage': float,
                'correct_answers': int,
                'total_questions': int,
                'time_taken_total': int,
                'mastery_updates': dict
            }
        """
```

### Quiz Types

1. **Random Quiz** (`quiz_type='random'`)
   - Select N random exercises from course
   - Prioritize due reviews if `prioritize_due=True`

2. **Topic Quiz** (`quiz_type='topic'`)
   - All questions from specific topic
   - Good for focused practice

3. **Core Loop Quiz** (`quiz_type='core_loop'`)
   - All questions using specific core loop
   - Master one algorithm at a time

4. **Review Quiz** (`quiz_type='review'`)
   - Only exercises due for review (SM-2)
   - Optimal for spaced repetition

**Estimated effort:** 4-5 hours

---

## Phase 5.4: CLI Commands

### Command: `examina quiz`

```bash
# Random quiz (10 questions, prioritize due reviews)
examina quiz --course ADE

# Custom number of questions
examina quiz --course ADE --questions 20

# Topic-focused quiz
examina quiz --course ADE --topic "Sequential Circuits"

# Core loop quiz
examina quiz --course ADE --loop moore_machine_design

# Review mode (only due exercises)
examina quiz --course ADE --review-only

# Difficulty filter
examina quiz --course ADE --difficulty hard

# Language
examina quiz --course AL --lang it
```

### Command: `examina progress`

```bash
# Overall course progress
examina progress --course ADE

# Topic-level breakdown
examina progress --course ADE --topics

# Core loop mastery
examina progress --course ADE --core-loops

# Detailed exercise-level data
examina progress --course ADE --detailed

# Show due reviews
examina progress --course ADE --due-reviews
```

### Command: `examina suggest`

```bash
# Suggest what to study next
examina suggest

# Suggest for specific course
examina suggest --course ADE

# Output:
# 📚 Study Suggestions for ADE:
#   1. Review Mode: 5 exercises due today
#   2. Weak Topic: "Sequential Circuits" (40% mastery)
#   3. New Topic: "Floating Point Arithmetic" (not started)
```

### Interactive Quiz Flow

```
$ examina quiz --course ADE --questions 5

🎯 Starting quiz for Computer Architecture (ADE)
   Questions: 5 | Prioritizing due reviews: Yes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Question 1/5 | Topic: Sequential Circuits | Difficulty: Medium

[Exercise text displayed]

Your answer (press Enter twice to finish):
> [User types answer]

⏱️  Time taken: 3m 24s

🤖 Evaluating your answer...

✅ Correct!

Feedback:
[AI-generated feedback on the answer quality]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Continue for all 5 questions...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Quiz Complete!

📊 Results:
   Score: 4/5 (80%)
   Time: 18m 32s
   Mastery updates:
   • Sequential Circuits: 40% → 52% (+12%)
   • Boolean Algebra: 65% → 70% (+5%)

📅 Next Review:
   • 2 exercises due tomorrow
   • 3 exercises due in 3 days
```

**Estimated effort:** 5-6 hours

---

## Phase 5.5: Progress Tracking & Analytics

### File: `core/analytics.py`

```python
class ProgressAnalytics:
    """Track and analyze learning progress."""

    def get_course_summary(self, course_code: str) -> Dict:
        """
        Get overall course progress.

        Returns:
            {
                'total_exercises': int,
                'exercises_attempted': int,
                'exercises_mastered': int,
                'overall_mastery': float,  # 0.0-1.0
                'quiz_sessions_completed': int,
                'total_time_spent_minutes': int,
                'average_score': float
            }
        """

    def get_topic_breakdown(self, course_code: str) -> List[Dict]:
        """
        Get mastery per topic.

        Returns list of:
            {
                'topic_name': str,
                'exercises_total': int,
                'exercises_mastered': int,
                'mastery_percentage': float,
                'last_practiced': datetime,
                'needs_review': bool
            }
        """

    def get_weak_areas(self, course_code: str, threshold: float = 0.5) -> List[Dict]:
        """Identify topics/core loops below mastery threshold."""

    def get_due_reviews(self, course_code: str) -> List[Dict]:
        """Get exercises due for review today."""

    def get_study_suggestions(self, course_code: Optional[str] = None) -> List[str]:
        """
        Generate personalized study suggestions.

        Priority order:
        1. Overdue reviews (should have been reviewed days ago)
        2. Due reviews (scheduled for today)
        3. Weak areas (low mastery, recently practiced)
        4. New content (never practiced)
        """

    def get_learning_curve(self, course_code: str, days: int = 30) -> Dict:
        """Get performance trend over time."""
```

### Display Format

```
$ examina progress --course ADE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Progress Report: Computer Architecture (ADE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall Progress:
  ██████████████████░░░░░░░░░░ 58% Mastery

  Exercises:     15/27 mastered
  Quiz Sessions: 8 completed
  Time Spent:    4h 23m
  Avg Score:     78%

Topic Breakdown:
  ✅ Boolean Algebra               ████████████████████ 85%
  ⚠️  Sequential Circuits          ██████████░░░░░░░░░░ 52%
  ⚠️  FSM Design                   ████████░░░░░░░░░░░░ 45%
  ❌ Floating Point Arithmetic     ░░░░░░░░░░░░░░░░░░░░  0%

Core Loop Mastery:
  ✅ Karnaugh Map Minimization     ████████████████████ 90%
  ✅ Moore Machine Design          ███████████████░░░░░ 75%
  ⚠️  Timing Diagram Analysis      ██████████░░░░░░░░░░ 50%
  ❌ IEEE 754 Encoding             ████░░░░░░░░░░░░░░░░ 20%

📅 Review Schedule:
  Today:     3 exercises due
  Tomorrow:  5 exercises due
  This week: 12 exercises due

💡 Suggestions:
  1. 🔴 Complete 3 overdue reviews
  2. 🟡 Practice "FSM Design" (weak area)
  3. 🟢 Start "Floating Point Arithmetic" (new topic)
```

**Estimated effort:** 4-5 hours

---

## Phase 5.6: Visualization (Optional Enhancement)

### Rich Terminal Charts

Use Rich library for in-terminal visualizations:

```python
from rich.table import Table
from rich.progress import BarColumn, Progress
from rich.panel import Panel

# Mastery bars
# Performance trends (sparklines)
# Color-coded topic status
```

### Export Options

```bash
# Export progress as JSON
examina progress --course ADE --export progress.json

# Export quiz history as CSV
examina progress --course ADE --export-csv quiz_history.csv
```

**Estimated effort:** 2-3 hours (if implemented)

---

## Testing Plan

### Unit Tests

1. **SM-2 Algorithm** (`tests/test_sm2.py`)
   - Test quality calculation
   - Test interval scheduling
   - Test EF adjustments
   - Edge cases (quality 0, quality 5, repetition limits)

2. **Quiz Manager** (`tests/test_quiz.py`)
   - Quiz creation (all types)
   - Question selection logic
   - Answer submission
   - Session completion

3. **Analytics** (`tests/test_analytics.py`)
   - Mastery calculation
   - Weak area identification
   - Study suggestions

### Integration Tests

1. **Full Quiz Flow**
   - Create quiz → Answer questions → Get feedback → Complete
   - Verify SM-2 updates
   - Check mastery level changes

2. **Multi-Session Progress**
   - Take multiple quizzes over "simulated days"
   - Verify intervals increase correctly
   - Check mastery progression

### Real-World Testing

1. Take actual quizzes on ADE, AL, PC courses
2. Verify mastery calculations make sense
3. Test review scheduling over several days
4. Validate study suggestions are helpful

**Estimated effort:** 4-5 hours

---

## Implementation Timeline

### Week 1: Database & Core Algorithm
- Day 1-2: Database schema + migrations
- Day 3-4: SM-2 algorithm implementation
- Day 5: Testing SM-2

### Week 2: Quiz System
- Day 6-7: QuizManager implementation
- Day 8-9: CLI commands (quiz, progress, suggest)
- Day 10: Interactive quiz flow

### Week 3: Analytics & Polish
- Day 11-12: Analytics implementation
- Day 13: Progress displays and visualizations
- Day 14-15: Integration testing + bug fixes

**Total estimated effort:** 35-45 hours (1-2 weeks of focused work)

---

## Success Criteria

✅ Users can take quizzes on any course
✅ SM-2 algorithm schedules reviews correctly
✅ Mastery levels update based on performance
✅ Progress tracking shows clear improvement over time
✅ Study suggestions help users focus on weak areas
✅ Review reminders prevent forgetting
✅ All features work in both Italian and English

---

## Future Enhancements (Phase 6?)

- **Gamification**: Streaks, achievements, leaderboards
- **Export to Anki**: Convert to Anki deck
- **Mobile notifications**: Review reminders
- **Study groups**: Compare progress with peers
- **AI difficulty adjustment**: Adaptive question difficulty
- **Performance prediction**: Estimate exam readiness

---

## Documentation Needed

- `QUIZ_SYSTEM.md` - User guide for quiz features
- `SM2_ALGORITHM.md` - Technical explanation of spaced repetition
- Update `README.md` with Phase 5 status
- Update `TODO.md` with Phase 5 subtasks

---

## Risk Assessment

**Low Risk:**
- Database schema changes (have migration system)
- SM-2 algorithm (well-documented, proven)

**Medium Risk:**
- Quiz question selection logic (needs good edge case handling)
- Analytics calculations (must be accurate)

**Mitigation:**
- Comprehensive unit tests
- Gradual rollout (start with simple features)
- User testing with real courses

---

## Dependencies

**New packages needed:**
- None! All required packages already installed

**Existing dependencies used:**
- Rich (for progress bars and charts)
- SQLite (for quiz/review data)
- Click (for CLI commands)

---

**Ready to start Phase 5 implementation whenever you are!** 🚀
