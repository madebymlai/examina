# examina-core

Core library for Examina - PDF processing, LLM analysis, SM2 algorithm, tutor/quiz engine.

## Rules

Follow rules in `/home/laimk/git/examina-cloud/.claude/rules.md`

## This Repo Contains

- `core/` - Business logic (analyzer, tutor, quiz_engine, sm2, pdf_processor)
- `models/` - LLM manager
- `storage/` - Database (SQLite for CLI), file manager
- `cli.py` - Command-line interface

## When to Add Code Here

- Analysis logic (topic detection, difficulty, core loops, source type)
- LLM prompts and AI features
- SM2/spaced repetition algorithm
- PDF parsing, exercise splitting
- Tutor/quiz engine features
- Any pure business logic

## When to Add Code to examina-cloud Instead

- API endpoints, database migrations
- Authentication, billing
- Frontend components
- Multi-tenant filtering
- Web-specific code

## Cross-Repo Changes

1. Add core logic here first
2. Test standalone
3. Then integrate in examina-cloud
4. Update TODO.md in both repos
