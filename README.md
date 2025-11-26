# Examina

AI-powered exam preparation system that learns from your course materials to help you master university courses.

## What It Does

Examina analyzes your course materials (past exams, homework, problem sets, lecture notes) to automatically:
- **Discover topics & procedures** - Identifies recurring problem-solving patterns ("core loops")
- **Build a knowledge base** - Extracts exercises, procedures, and solving strategies
- **Teach adaptively** - AI tutoring that adjusts depth based on your mastery level
- **Track progress** - Uses spaced repetition (SM-2) with mastery cascade updates
- **Enforce prerequisites** - Warns when foundational concepts need review
- **Generate practice** - Creates mastery-based quizzes prioritizing weak areas

## Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/madebymlai/examina.git
cd Examina
python -m venv venv
source venv/bin/activate  # Linux/Mac | Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure LLM providers (set the ones you want to use)
export DEEPSEEK_API_KEY="your-key"   # Recommended for bulk analysis (cheapest)
export GROQ_API_KEY="your-key"       # Recommended for quizzes (fast)
export ANTHROPIC_API_KEY="your-key"  # Optional - premium explanations

# Choose a provider profile
export EXAMINA_PROVIDER_PROFILE=free  # free|pro|local

# Initialize database
python3 cli.py init
```

**Provider Profiles:**
- `free` - DeepSeek for analysis, Groq for quizzes (cost-effective)
- `pro` - DeepSeek for analysis, Anthropic for explanations (best quality)
- `local` - Ollama only (private, requires local GPU)

### Basic Usage

```bash
# 1. Add a course
python3 cli.py add-course --code ADE --name "Computer Architecture"

# 2. Ingest course materials (past exams, homework, problem sets, etc.)
python3 cli.py ingest --course ADE --zip course_materials.zip

# 3. Analyze with AI (discovers topics & procedures)
python3 cli.py analyze --course ADE --profile free

# 4. View what was learned
python3 cli.py info --course ADE
python3 cli.py concept-map --course ADE  # Visual concept hierarchy

# 5. Start learning (adaptive depth based on mastery)
python3 cli.py learn --course ADE --loop "Mealy Machine Design"

# 6. Take an adaptive quiz (prioritizes weak areas)
python3 cli.py quiz --course ADE --questions 5 --adaptive

# 7. Check progress
python3 cli.py progress --course ADE
```

## What Can You Upload?

Examina works with **any course material containing problems and exercises**:

- ✅ **Past Exams** - With or without solutions (best for discovering exam patterns)
- ✅ **Homework Assignments** - Problem sets from professors or TAs
- ✅ **Practice Exams** - Mock exams or practice problems
- ✅ **Exercise Collections** - PDFs from course websites or textbooks
- ✅ **Lecture Notes** - Notes with worked examples and practice problems
- ✅ **Problem Set PDFs** - Any structured problem collection

**The engine learns from structure, not source.** Past exams are ideal but not required.

**Best Results With:**
- Clearly numbered exercises ("Exercise 1", "Problem 2", "1.", "2)")
- Structured problem sets with consistent formatting
- Mixed language support (Italian, English, Spanish, French, etc.)

**Coming Soon:** Advanced splitting for unstructured lecture notes and embedded examples.

## Key Features

### 🎯 Smart Analysis
- Automatically discovers topics and core loops (solving procedures)
- Extracts multi-step procedures from complex exercises
- Supports theory questions, proofs, and procedural exercises
- Works across any subject (Computer Science, Math, Engineering, etc.)

### 🧠 Adaptive AI Tutoring
- **Adaptive depth** - Explanation complexity adjusts to your mastery level
- **Prerequisite enforcement** - Warns when foundational concepts need review
- **Real-time feedback** - Shows mastery progress after each quiz answer
- **Personalized learning paths** - Recommends what to study next

### 📊 Mastery Tracking
- SM-2 spaced repetition with cascade updates (exercise → topic → course)
- Mastery levels: new → learning → reviewing → mastered
- **Concept map visualization** - See topic/core loop hierarchy with mastery
- **Weak area detection** - Automatically identifies gaps in knowledge

### 🎮 Adaptive Quizzes
- **Mastery-based selection** - 40% weak, 40% learning, 20% strong exercises
- **Prerequisite awareness** - Shows tips when prerequisites are weak
- Filter by topic, difficulty, procedure type, or exercise type

### 🌐 Multi-Language
- Full Italian/English support
- Bilingual deduplication (merges "Finite State Machine" ↔ "Macchina a Stati Finiti")

### ⚡ Performance & Cost
- **Provider routing** - Automatically uses cheapest provider per task type
- **Procedure pattern caching** - 100% cache hit rate on re-analysis
- **Async/await analysis** - 1.1-5x faster with concurrent LLM calls
- **26+ exercises/second** with cached patterns

## Commands Reference

### Course Management
```bash
python3 cli.py add-course --code B006802 --name "Architettura degli Elaboratori"
python3 cli.py list-courses
python3 cli.py info --course B006802
python3 cli.py concept-map --course B006802              # Visual hierarchy
python3 cli.py concept-map --course B006802 --show-mastery  # With progress
```

### Content Ingestion
```bash
# From ZIP archive (past exams, homework, problem sets, lecture notes, etc.)
python3 cli.py ingest --course B006802 --zip course_materials.zip

# From directory
python3 cli.py ingest --course B006802 --dir ./course_pdfs/

# Examples of what you can ingest:
# - Past exams with or without solutions
# - Homework assignments and problem sets
# - Practice exams from the professor
# - Exercise collections from course sites
# - Lecture notes with worked examples
# - Textbook problem PDFs
```

### Analysis
```bash
# Analyze with provider profile (recommended)
python3 cli.py analyze --course B006802 --profile free --lang it

# Or specify provider directly
python3 cli.py analyze --course B006802 --provider deepseek

# Resume interrupted analysis
python3 cli.py analyze --course B006802 --resume

# Force re-analysis
python3 cli.py analyze --course B006802 --force
```

### Learning
```bash
# Learn a specific procedure (adaptive depth based on mastery)
python3 cli.py learn --course B006802 --loop "Moore Machine Design"

# Manual depth control
python3 cli.py learn --course B006802 --loop "Mealy Machine Design" --depth advanced

# Skip prerequisite check
python3 cli.py learn --course B006802 --loop "FSM Minimization" --force

# Skip prerequisite explanations
python3 cli.py learn --course B006802 --loop "FSM Minimization" --no-concepts
```

### Quizzes
```bash
# Adaptive quiz (prioritizes weak areas - recommended)
python3 cli.py quiz --course B006802 --questions 10 --adaptive

# Random quiz
python3 cli.py quiz --course B006802 --questions 10

# Filtered quiz
python3 cli.py quiz --course B006802 --topic "Automi a Stati Finiti" --difficulty medium

# Review mode (spaced repetition)
python3 cli.py quiz --course B006802 --review-only

# Filter by exercise type
python3 cli.py quiz --course B006802 --type theory
python3 cli.py quiz --course B006802 --type proof
```

### Progress & Analytics
```bash
# Overall progress
python3 cli.py progress --course B006802

# Study suggestions
python3 cli.py suggest --course B006802
```

### Maintenance
```bash
# Deduplicate topics/core loops
python3 cli.py deduplicate --course B006802 --dry-run

# Split generic topics
python3 cli.py split-topics --course B006802 --dry-run

# Manage procedure cache (for faster re-analysis)
python3 cli.py pattern-cache --stats           # View cache stats
python3 cli.py pattern-cache --build           # Build cache from analyzed exercises
python3 cli.py pattern-cache --clear           # Clear cache entries
```

## Configuration

### Provider Profiles (Recommended)

Use `--profile` to automatically route tasks to optimal providers:

```bash
python3 cli.py analyze --course ADE --profile free
python3 cli.py quiz --course ADE --profile pro
```

| Profile | Bulk Analysis | Interactive | Premium |
|---------|---------------|-------------|---------|
| `free`  | DeepSeek      | Groq        | Disabled |
| `pro`   | DeepSeek      | Anthropic   | Anthropic |
| `local` | Ollama        | Ollama      | Ollama |

### LLM Providers

**DeepSeek** (Recommended for bulk)
- 671B MoE model, excellent reasoning
- $0.14/M tokens (10-20x cheaper than Anthropic)
- No rate limiting
- `--provider deepseek`

**Groq** (Free tier available)
- Fast inference
- 30 requests/minute free tier
- `--provider groq`

**Anthropic Claude** (Premium quality)
- Best explanations and reasoning
- Higher cost
- `--provider anthropic`

**Ollama** (Local)
- Free and private
- Requires local GPU
- `--provider ollama`

### Environment Variables

```bash
# Provider Profile (recommended)
export EXAMINA_PROVIDER_PROFILE=free   # free|pro|local

# API Keys (set the ones you need)
export DEEPSEEK_API_KEY="your-key"
export GROQ_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Analysis Settings
export EXAMINA_MIN_CONFIDENCE=0.5      # Filter low-confidence analyses
export EXAMINA_PARALLEL_WORKERS=4      # Parallel analysis workers

# Topic Splitting
export EXAMINA_GENERIC_TOPIC_THRESHOLD=10  # Min core loops to trigger split
export EXAMINA_TOPIC_SPLITTING_ENABLED=1

# Deduplication
export EXAMINA_SIMILARITY_THRESHOLD=0.85
export EXAMINA_SEMANTIC_MATCHING=1
```

## Project Status

**Production Ready (CLI Complete):**
- ✅ PDF ingestion & extraction
- ✅ AI analysis & knowledge discovery
- ✅ Interactive AI tutor with adaptive depth
- ✅ Quiz system with spaced repetition
- ✅ Multi-procedure extraction
- ✅ Automatic topic splitting
- ✅ Theory & proof support
- ✅ Bilingual deduplication
- ✅ Procedure pattern caching (v0.14.0)
- ✅ Async/await analysis pipeline (v0.13.0)
- ✅ Adaptive teaching based on mastery (v0.15.0)
- ✅ Prerequisite enforcement
- ✅ Provider routing (free/pro/local profiles)
- ✅ Concept map visualization

**Planned:**
- 📋 Web application interface

See [TODO.md](TODO.md) for detailed task list and [CHANGELOG.md](CHANGELOG.md) for version history.

## Architecture

```
Examina/
├── cli.py                  # Main CLI interface
├── config.py               # Configuration management
├── core/                   # Core modules
│   ├── analyzer.py         # Exercise analysis
│   ├── tutor.py            # AI teaching
│   ├── quiz_engine.py      # Quiz system with adaptive selection
│   ├── sm2.py              # Spaced repetition
│   ├── mastery_aggregator.py   # Mastery cascade updates
│   ├── adaptive_teaching.py    # Prerequisite enforcement
│   ├── semantic_matcher.py     # Deduplication
│   ├── procedure_cache.py      # Pattern caching
│   ├── provider_router.py      # Task-based provider routing
│   └── task_types.py           # Task type definitions
├── models/                 # LLM integrations
│   └── llm_manager.py      # Provider abstraction
├── storage/                # Data layer
│   └── database.py         # SQLite + migrations
├── config/                 # Configuration files
│   └── provider_profiles.yaml  # Provider routing profiles
└── utils/                  # Utilities
    ├── pdf_extractor.py
    └── splitter.py
```

## Contributing

Issues and pull requests welcome! See [TODO.md](TODO.md) for areas needing work.

## Privacy & Data

**Your course materials stay yours.** Examina analyzes the materials you upload (exams, homework, problem sets, notes) to build a private knowledge base for you only. We don't share your materials or generated questions with other users.

- 📄 Your PDFs are stored locally in your account
- 🔒 Content sent to LLM providers only for generating explanations/quizzes
- 🚫 We don't sell data or train models on your course materials
- 🗑️ Delete your uploads and data anytime

See [PRIVACY.md](PRIVACY.md) for full details.

## License

MIT License - see LICENSE file for details.

## Credits

Built with Claude Code by Anthropic.
