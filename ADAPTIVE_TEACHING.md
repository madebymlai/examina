# Adaptive Teaching System - Phase 7.4

## Overview

The Adaptive Teaching System personalizes explanations and learning paths based on the student's understanding level and learning progress. It leverages existing SM-2 mastery data from Phase 5 to provide intelligent recommendations.

## Features Implemented

### 1. Core Module: `core/adaptive_teaching.py`

**AdaptiveTeachingManager** class with the following capabilities:

#### Understanding Tracker
- Tracks student understanding per topic using SM-2 mastery data
- Calculates mastery scores (0.0-1.0) from `student_progress` table
- Aggregates mastery across topics and core loops

#### Depth Auto-Adjuster
Automatically selects explanation depth based on mastery level:
- **Basic** (mastery < 0.3): Simple, concise explanations for beginners
- **Medium** (0.3 ≤ mastery < 0.7): Balanced explanations with WHY reasoning
- **Advanced** (mastery ≥ 0.7): Comprehensive explanations with edge cases

#### Knowledge Gap Detector
Identifies missing prerequisite knowledge:
- Analyzes mastery levels across all core loops
- Classifies gaps by severity (high/medium/low)
- Provides actionable recommendations

#### Learning Path Generator
Recommends personalized study sequences:
1. **Overdue reviews** (highest priority) - SM-2 scheduled reviews past due
2. **Weak areas** - Core loops with mastery < 0.5
3. **Due reviews** - Reviews scheduled for today
4. **New content** - Core loops not yet attempted

### 2. Integration with Tutor (`core/tutor.py`)

Enhanced `learn()` method with adaptive parameter:
```python
tutor.learn(
    course_code="B006802",
    core_loop_id="karnaugh_map_minimization",
    adaptive=True  # Auto-selects depth and prerequisites
)
```

**Adaptive Behavior:**
- Automatically determines optimal explanation depth
- Decides whether to show prerequisites based on mastery and recent failures
- Appends personalized recommendations at end of explanations

### 3. Integration with Analytics (`core/analytics.py`)

Added methods for adaptive decisions:
- `calculate_topic_mastery()` - Calculate topic mastery score (0.0-1.0)
- `get_quiz_performance_data()` - Expose quiz performance for analysis

### 4. CLI Integration (`cli.py`)

#### Modified `learn` Command
```bash
# Adaptive mode (default)
examina learn --course ADE --loop karnaugh_map_minimization

# Disable adaptive (manual control)
examina learn --course ADE --loop karnaugh_map_minimization --no-adaptive --depth advanced
```

#### New `path` Command
```bash
# Show personalized learning path
examina path --course ADE

# Limit number of items
examina path --course ADE --limit 5
```

**Output Example:**
```
📚 Personalized Learning Path

#  Action          Core Loop                     Topic           Reason                      Time
1  🔄 Review       Moore Machine Design          FSM Design      Overdue by 3 days           15m
2  💪 Strengthen   Karnaugh Map Minimization     Boolean Alg.    Low mastery (45%)           20m
3  🔄 Review       State Table Construction      FSM Design      Due for review              15m
4  📖 Learn        Circuit Implementation        Hardware        New content (8 exercises)   25m
```

#### New `gaps` Command
```bash
# Identify knowledge gaps
examina gaps --course ADE

# Filter by specific core loop
examina gaps --course ADE --loop karnaugh_map_minimization
```

**Output Example:**
```
🔍 Knowledge Gaps Analysis

⚠️  High Priority Gaps

  • Boolean Algebra Fundamentals (Boolean Algebra)
    Mastery: 18%
    💡 Review Boolean algebra fundamentals before continuing with advanced topics
    Affects: Karnaugh Map Minimization, Logic Simplification

⚡ Medium Priority Gaps

  • State Transition Tables (FSM Design) - 42% mastery
    💡 Practice State transition table exercises to strengthen understanding

Summary:
  Total gaps found: 5
  High priority: 2
  Medium priority: 2
  Low priority: 1
```

## Mastery-to-Depth Mapping

| Mastery Level | Depth | Prerequisites | Practice Count |
|--------------|-------|---------------|----------------|
| < 30% (New/Learning) | Basic | Always show | 5 exercises |
| 30-70% (Reviewing) | Medium | Show if recent failures | 3 exercises |
| ≥ 70% (Mastered) | Advanced | Skip | 1 exercise |

## Knowledge Gap Detection Logic

**Severity Levels:**
- **High** (mastery < 0.2): Critical gaps, must address immediately
- **Medium** (0.2 ≤ mastery < 0.35): Important gaps, should strengthen
- **Low** (0.35 ≤ mastery < 0.5): Minor gaps, optional improvement

**Detection Criteria:**
1. Check prerequisite mastery vs. current topic mastery
2. Analyze recent quiz failure rates (> 40% incorrect)
3. Identify core loops not practiced recently

## Learning Path Priority Algorithm

1. **Overdue Reviews** - Past due date from SM-2 algorithm
   - Urgency: High
   - Time: 15 minutes
   - Sorted by: Days overdue (descending)

2. **Weak Areas** - Mastery < 0.5
   - Urgency: Medium
   - Time: 20 minutes
   - Sorted by: Mastery score (ascending)

3. **Due Reviews** - Scheduled for today
   - Urgency: Medium
   - Time: 15 minutes
   - Sorted by: Mastery score (ascending)

4. **New Content** - Not yet attempted
   - Urgency: Low
   - Time: 25 minutes
   - Sorted by: Difficulty (easy first), then exercise count

## Example Scenarios

### Scenario 1: Beginner Student (Alice)

**Profile:**
- Overall mastery: 15%
- Just started course
- No quizzes completed yet

**Adaptive Behavior:**
- Depth: **Basic**
- Prerequisites: **Always shown**
- Practice: **5 exercises recommended**
- Learning path: Focuses on new content with simple exercises

### Scenario 2: Intermediate Student (Bob)

**Profile:**
- Overall mastery: 55%
- Completed 10 quizzes
- Some weak areas in Boolean algebra

**Adaptive Behavior:**
- Depth: **Medium**
- Prerequisites: **Shown if recent failures**
- Practice: **3 exercises recommended**
- Learning path: Mix of reviews and weak area practice

**Detected Gaps:**
- Boolean Algebra (mastery: 42%) - Medium priority
- Karnaugh Maps (mastery: 38%) - Medium priority

### Scenario 3: Advanced Student (Carol)

**Profile:**
- Overall mastery: 85%
- Completed 25 quizzes
- Strong across all topics

**Adaptive Behavior:**
- Depth: **Advanced**
- Prerequisites: **Skipped**
- Practice: **1 exercise for maintenance**
- Learning path: Primarily scheduled reviews

## Data Integration

The system uses existing Phase 5 data structures:

### Tables Used:
- `student_progress` - SM-2 data (mastery_score, next_review, interval)
- `quiz_attempts` - Individual question performance
- `topic_mastery` - Aggregated mastery per topic
- `exercise_reviews` - SM-2 review schedule

### No New Tables Required
All adaptive features leverage existing data structures, ensuring seamless integration.

## API Examples

### Python API

```python
from core.adaptive_teaching import AdaptiveTeachingManager

# Initialize manager
with AdaptiveTeachingManager() as atm:
    # Get recommended depth
    depth = atm.get_recommended_depth(
        course_code="B006802",
        core_loop_name="Karnaugh Map Minimization"
    )
    # Returns: 'basic', 'medium', or 'advanced'

    # Check if prerequisites should be shown
    show_prereqs = atm.should_review_prerequisites(
        course_code="B006802",
        core_loop_name="Karnaugh Map Minimization"
    )
    # Returns: True or False

    # Detect knowledge gaps
    gaps = atm.detect_knowledge_gaps(
        course_code="B006802"
    )
    # Returns: List of gap dictionaries

    # Get personalized learning path
    path = atm.get_personalized_learning_path(
        course_code="B006802",
        limit=10
    )
    # Returns: List of learning path items

    # Get adaptive recommendations
    recommendations = atm.get_adaptive_recommendations(
        course_code="B006802",
        core_loop_name="Karnaugh Map Minimization"
    )
    # Returns: {depth, show_prerequisites, practice_count, focus_areas, ...}
```

### CLI Usage

```bash
# Learn with adaptive mode (default)
examina learn --course ADE --loop karnaugh_map_minimization

# Learn with manual depth control
examina learn --course ADE --loop karnaugh_map_minimization \
    --no-adaptive --depth basic --no-concepts

# View personalized learning path
examina path --course ADE --limit 10

# Identify knowledge gaps
examina gaps --course ADE

# View progress with adaptive insights
examina progress --course ADE --detailed
```

## Language Support

The system supports both Italian and English:

```python
# English (default)
tutor = Tutor(language="en")

# Italian
tutor = Tutor(language="it")
```

**Recommendation Headers (Italian):**
- "RACCOMANDAZIONI DI STUDIO PERSONALIZZATE"
- "Livello di padronanza attuale"
- "Esercizi consigliati per la pratica"
- "Aree su cui concentrarsi"

## Performance Considerations

1. **Database Queries**: Optimized with proper indexing on `student_progress`
2. **Caching**: Mastery calculations cached to avoid redundant queries
3. **Lazy Loading**: Only fetch data when needed
4. **Batch Operations**: Process multiple recommendations in single DB connection

## Future Enhancements

Potential improvements for future versions:

1. **Multi-user Support**: Add user_id parameter throughout
2. **Prerequisite Graph**: Build explicit prerequisite relationships
3. **Learning Style Detection**: Adapt to visual/textual/practical learners
4. **Time-based Adaptation**: Consider time-of-day and session length
5. **Peer Comparison**: Compare progress with similar students
6. **Confidence Tracking**: Track student self-assessment
7. **Difficulty Adjustment**: Dynamic difficulty based on performance

## Testing

Run the example demonstrations:

```bash
# View examples
python examples/adaptive_examples.py

# Test with real course data (requires existing database)
python -c "
from examples.adaptive_examples import *
example_learning_path('B006802')
example_knowledge_gaps('B006802')
example_adaptive_recommendations('B006802')
"
```

## Implementation Summary

**Files Created:**
1. `core/adaptive_teaching.py` (~600 lines) - Core adaptive teaching logic

**Files Modified:**
1. `core/tutor.py` - Added adaptive parameter and recommendations
2. `core/analytics.py` - Added mastery calculation methods
3. `cli.py` - Added `path` and `gaps` commands, modified `learn` command

**Files Added:**
1. `examples/adaptive_examples.py` - Demonstration examples
2. `ADAPTIVE_TEACHING.md` - This documentation

**Total Lines Added:** ~1200 lines
**New Dependencies:** None (uses existing libraries)
