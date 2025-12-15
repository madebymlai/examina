# Examina Core

Core business logic for AI-powered exam preparation.

## What It Does

- **Exercise Analysis** - Extracts knowledge items from PDFs
- **Smart Splitting** - Detects exercises, sub-questions, solutions
- **Adaptive Tutoring** - AI tutoring that adjusts to mastery level
- **Spaced Repetition** - SM2 algorithm for optimal retention
- **Quiz Engine** - Generates practice quizzes

## Architecture

```
examina (this repo)     - Core logic, lightweight
    ↓ used by
examina-cloud           - Web platform (FastAPI + React)
examina-cli             - Local CLI tool (separate repo)
```

## Installation

```bash
pip install git+https://github.com/madebymlai/examina.git
```

Or for development:
```bash
git clone https://github.com/madebymlai/examina.git
cd examina
pip install -e .
```

## Usage

```python
from core.analyzer import ExerciseAnalyzer, generate_item_description
from core.tutor import Tutor
from core.quiz_engine import QuizEngine
from core.pdf_processor import PDFProcessor
from models.llm_manager import LLMManager

# Initialize
llm = LLMManager()

# Analyze an exercise
analyzer = ExerciseAnalyzer(llm_manager=llm, language="en")
result = analyzer.analyze_exercise(
    exercise_text="Prove that the sum of two even numbers is even.",
    course_name="Discrete Math"
)
print(result.knowledge_items)  # [KnowledgeItemInfo(name='even_number_properties', ...)]

# Generate learning content
tutor = Tutor(llm_manager=llm, language="en")
explanation = await tutor.explain_concept(
    knowledge_item_name="even_number_properties",
    exercises=[...],
    learning_approach="conceptual"
)
```

## Modules

| Module | Purpose |
|--------|---------|
| `core/analyzer.py` | Exercise analysis, knowledge extraction |
| `core/tutor.py` | Adaptive explanations |
| `core/quiz_engine.py` | Quiz generation and scoring |
| `core/review_engine.py` | Answer evaluation |
| `core/sm2.py` | Spaced repetition algorithm |
| `core/pdf_processor.py` | PDF text extraction |
| `core/exercise_splitter.py` | Exercise detection |

## LLM Providers

| Provider  | Best For |
|-----------|----------|
| DeepSeek  | Analysis, grouping (deepseek-reasoner) |
| Groq      | Fast responses |
| Anthropic | Premium explanations |

## Related

- [examina-cloud](https://github.com/madebymlai/examina-cloud) - Web platform
- [examina-cli](https://github.com/madebymlai/examina-cli) - Local CLI tool

## License

MIT License
