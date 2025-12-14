# Examina

AI-powered exam preparation that learns from your course materials.

## What It Does

Upload past exams, homework, or problem sets. Examina analyzes them to:

- **Discover knowledge** - Identifies concepts, procedures, theorems, and formulas
- **Smart merging** - Groups equivalent items across PDFs using AI reasoning
- **Teach adaptively** - AI tutoring that adjusts to your mastery level
- **Track progress** - Spaced repetition with SM2 algorithm
- **Generate practice** - Quizzes that prioritize weak areas

## Quick Start

```bash
# Setup
git clone https://github.com/madebymlai/examina.git
cd examina
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure (set at least one)
export DEEPSEEK_API_KEY="your-key"  # Best for bulk analysis
export GROQ_API_KEY="your-key"      # Fast, free tier available

# Initialize
python3 cli.py init
```

## Usage

```bash
# 1. Create course
python3 cli.py add-course --code ADE --name "Computer Architecture"

# 2. Upload materials (exams, homework, problem sets)
python3 cli.py ingest --course ADE --zip materials.zip

# 3. Analyze (discovers knowledge items)
python3 cli.py analyze --course ADE

# 4. Learn a topic
python3 cli.py learn --course ADE --item "matrix_diagonalization"

# 5. Take adaptive quiz
python3 cli.py quiz --course ADE --questions 10 --adaptive

# 6. Check progress
python3 cli.py progress --course ADE
```

## What Can You Upload?

Any PDF with numbered exercises (max 20 pages):
- Past exams (with or without solutions)
- Homework assignments
- Practice problem sets
- Exercise collections

**Works with any language** - Italian, English, Spanish, French, etc.

## Features

### Analysis
- Language-agnostic exercise detection
- Smart sub-question splitting
- Knowledge item extraction (procedures, theorems, definitions, formulas)
- DeepSeek reasoner for accurate item grouping

### Learning
- Adaptive depth based on mastery
- Learning approach detection (procedural, conceptual, factual, analytical)
- Real-time feedback

### Progress
- SM-2 spaced repetition
- Mastery tracking per knowledge item
- Weak area detection
- Study suggestions

### Performance
- Provider routing (cheapest per task type)
- Response caching (faster re-analysis)
- Async analysis pipeline

## LLM Providers

| Provider  | Best For                   | Model |
|-----------|----------------------------|-------|
| DeepSeek  | Analysis, grouping         | deepseek-chat, deepseek-reasoner |
| Groq      | CLI quizzes (30 RPM limit) | Free tier available |
| Anthropic | Premium explanations       | Claude |
| Ollama    | Local, private             | Free (requires GPU) |

## Web Version

For multi-user web deployment, see [examina-cloud](https://github.com/madebymlai/examina-cloud).

## Privacy

Your materials stay local. Content is only sent to LLM providers for analysis. We don't train on your data.

## License

MIT License
