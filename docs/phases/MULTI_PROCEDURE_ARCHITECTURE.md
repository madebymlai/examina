# Multi-Procedure Architecture

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Exercise Text                            │
│  "1. Design Mealy machine                                        │
│   2. Convert to Moore                                            │
│   3. Minimize states"                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Analysis (New Prompt)                     │
│  - Detect ALL procedures                                         │
│  - Identify transformations                                      │
│  - Classify procedure types                                      │
│  - Extract numbered points                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Response (JSON)                           │
│  {                                                                │
│    "procedures": [                                               │
│      {                                                            │
│        "name": "Mealy Machine Design",                           │
│        "type": "design",                                         │
│        "steps": [...],                                           │
│        "point_number": 1                                         │
│      },                                                           │
│      {                                                            │
│        "name": "Mealy to Moore Transformation",                  │
│        "type": "transformation",                                 │
│        "steps": [...],                                           │
│        "point_number": 2,                                        │
│        "transformation": {                                       │
│          "source_format": "Mealy Machine",                       │
│          "target_format": "Moore Machine"                        │
│        }                                                          │
│      },                                                           │
│      {                                                            │
│        "name": "State Minimization",                             │
│        "type": "minimization",                                   │
│        "steps": [...],                                           │
│        "point_number": 3                                         │
│      }                                                            │
│    ]                                                              │
│  }                                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Parse & Create AnalysisResult                   │
│  - Convert to ProcedureInfo objects                              │
│  - Maintain backward compatibility properties                    │
│  - Generate tags from procedure types                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database Storage                              │
│                                                                   │
│  exercises table:                                                │
│  ┌────────────────────────────────────────────┐                 │
│  │ id: "ex123"                                 │                 │
│  │ topic_id: 5                                 │                 │
│  │ core_loop_id: "mealy_machine_design" ◄──────┼── PRIMARY       │
│  │ tags: ["design", "transformation", ...]     │                 │
│  │ analyzed: 1                                 │                 │
│  └────────────────────────────────────────────┘                 │
│                         │                                         │
│                         ▼                                         │
│  exercise_core_loops (junction table):                           │
│  ┌────────────────────────────────────────────┐                 │
│  │ exercise_id: "ex123"                        │                 │
│  │ core_loop_id: "mealy_machine_design"        │                 │
│  │ step_number: 1                              │                 │
│  ├────────────────────────────────────────────┤                 │
│  │ exercise_id: "ex123"                        │                 │
│  │ core_loop_id: "mealy_to_moore_transformation"│                │
│  │ step_number: 2                              │                 │
│  ├────────────────────────────────────────────┤                 │
│  │ exercise_id: "ex123"                        │                 │
│  │ core_loop_id: "state_minimization"          │                 │
│  │ step_number: 3                              │                 │
│  └────────────────────────────────────────────┘                 │
│                         │                                         │
│                         ▼                                         │
│  core_loops table:                                               │
│  ┌────────────────────────────────────────────┐                 │
│  │ id: "mealy_machine_design"                  │                 │
│  │ name: "Mealy Machine Design"                │                 │
│  │ type: "design"                              │                 │
│  │ procedure: [...]                            │                 │
│  ├────────────────────────────────────────────┤                 │
│  │ id: "mealy_to_moore_transformation"         │                 │
│  │ name: "Mealy to Moore Transformation"       │                 │
│  │ type: "transformation"                      │                 │
│  │ transformation: {...}                       │                 │
│  │ procedure: [...]                            │                 │
│  ├────────────────────────────────────────────┤                 │
│  │ id: "state_minimization"                    │                 │
│  │ name: "State Minimization"                  │                 │
│  │ type: "minimization"                        │                 │
│  │ procedure: [...]                            │                 │
│  └────────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Class Structure

```
AnalysisResult
├── is_valid_exercise: bool
├── is_fragment: bool
├── should_merge_with_previous: bool
├── topic: str
├── difficulty: str
├── variations: List[str]
├── confidence: float
├── procedures: List[ProcedureInfo]  ◄── NEW: Multiple procedures
│
└── Backward Compatibility Properties:
    ├── core_loop_id → procedures[0].name (normalized)
    ├── core_loop_name → procedures[0].name
    └── procedure → procedures[0].steps

ProcedureInfo
├── name: str
├── type: str  (design|transformation|verification|minimization|analysis|other)
├── steps: List[str]
├── point_number: Optional[int]  (1, 2, 3, ...)
└── transformation: Optional[Dict]
    ├── source_format: str
    └── target_format: str
```

## Query Patterns

### Old Way (Still Works)
```python
# Get exercises by primary core loop
exercises = db.get_exercises_by_core_loop("mealy_machine_design")

# Access primary procedure
analysis = analyzer.analyze_exercise(text)
print(analysis.core_loop_name)  # "Mealy Machine Design"
```

### New Way (Multi-Procedure)
```python
# Get ALL core loops for an exercise
core_loops = db.get_exercise_core_loops("ex123")
# Returns: [
#   {"id": "mealy_machine_design", "step_number": 1, ...},
#   {"id": "mealy_to_moore_transformation", "step_number": 2, ...},
#   {"id": "state_minimization", "step_number": 3, ...}
# ]

# Get exercises with multiple procedures
multi_exercises = db.get_exercises_with_multiple_procedures("B006802")

# Search by tags
transformation_exercises = [e for e in exercises if "transformation" in e.get("tags", [])]
mealy_to_moore = [e for e in exercises if "transform_mealy_machine_to_moore_machine" in e.get("tags", [])]

# Access all procedures
analysis = analyzer.analyze_exercise(text)
for proc in analysis.procedures:
    print(f"{proc.name} ({proc.type})")
    if proc.transformation:
        print(f"  {proc.transformation['source_format']} → {proc.transformation['target_format']}")
```

## Tag System

Tags are automatically generated from procedures:

```
Procedure Type → Tag
─────────────────────────────────────
design           → "design"
transformation   → "transformation"
verification     → "verification"
minimization     → "minimization"
analysis         → "analysis"

Transformation → Special Tag
─────────────────────────────────────
Mealy → Moore    → "transform_mealy_machine_to_moore_machine"
SOP → POS        → "transform_sop_to_pos"
DFA → Regex      → "transform_dfa_to_regex"
```

## Benefits Visualization

```
┌──────────────────────────────────────────────────────────────┐
│                     OLD SYSTEM                                │
├──────────────────────────────────────────────────────────────┤
│ Exercise: "1. Design Mealy, 2. Convert to Moore, 3. Minimize"│
│                                                               │
│ Stored as:                                                    │
│   core_loop_id: "mealy_machine_design"  ◄── Only first!      │
│                                                               │
│ Result: 66% of exercise content LOST                          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     NEW SYSTEM                                │
├──────────────────────────────────────────────────────────────┤
│ Exercise: "1. Design Mealy, 2. Convert to Moore, 3. Minimize"│
│                                                               │
│ Stored as:                                                    │
│   core_loop_id: "mealy_machine_design"  ◄── Primary (compat) │
│   Links:                                                      │
│     1. mealy_machine_design (point 1)                         │
│     2. mealy_to_moore_transformation (point 2)                │
│     3. state_minimization (point 3)                           │
│   Tags: ["design", "transformation", "minimization",          │
│          "transform_mealy_machine_to_moore_machine"]          │
│                                                               │
│ Result: 100% of exercise content CAPTURED                     │
└──────────────────────────────────────────────────────────────┘
```

## Procedure Type Classification

```
┌─────────────────────┬──────────────────────────────────────────┐
│ Type                │ Examples                                  │
├─────────────────────┼──────────────────────────────────────────┤
│ design              │ - Design Mealy machine                    │
│                     │ - Design 4-bit adder                      │
│                     │ - Create truth table                      │
├─────────────────────┼──────────────────────────────────────────┤
│ transformation      │ - Mealy → Moore conversion                │
│                     │ - SOP → POS conversion                    │
│                     │ - DFA → Regular expression                │
├─────────────────────┼──────────────────────────────────────────┤
│ verification        │ - Verify FSM equivalence                  │
│                     │ - Test circuit functionality              │
│                     │ - Validate expression correctness         │
├─────────────────────┼──────────────────────────────────────────┤
│ minimization        │ - State minimization                      │
│                     │ - Karnaugh map simplification             │
│                     │ - Boolean algebra reduction               │
├─────────────────────┼──────────────────────────────────────────┤
│ analysis            │ - Analyze timing diagram                  │
│                     │ - Determine logic function                │
│                     │ - Extract Boolean expression              │
├─────────────────────┼──────────────────────────────────────────┤
│ other               │ - Unknown or mixed procedures             │
│                     │ - Old format (type not specified)         │
└─────────────────────┴──────────────────────────────────────────┘
```
