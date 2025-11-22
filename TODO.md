# Examina - TODO List

## Phase 3 Improvements (Current)

### High Priority
- [ ] **Provider-agnostic rate limiting** - Class-level request tracker that works for all LLM providers
  - Track timestamps of recent requests
  - Configurable limits per provider (Groq: 25/min, OpenAI: 60/min, Anthropic: 50/min, Ollama: unlimited)
  - Auto-throttle before making requests (preventive vs reactive)
  - Estimated time for batch operations

### Medium Priority
- [ ] **Resume failed analysis** - Store analysis progress, resume from last successful exercise
- [ ] **Batch processing optimization** - Analyze exercises in optimal batch sizes for each provider
- [ ] **Caching** - Cache LLM responses to avoid re-analyzing same exercises

### Low Priority
- [ ] **Topic/core loop deduplication** - Merge similar topics ("Boolean Algebra" vs "Boolean Algebra and Digital Circuits")
- [ ] **Confidence thresholds** - Only store analysis if confidence > 0.7
- [ ] **Multi-provider fallback** - Try Ollama if Groq fails, or vice versa

## Phase 4 - Tutor Features (Next)
- [ ] Implement `learn` command - Interactive tutor for learning core loops
- [ ] Implement `practice` command - Practice exercises with hints
- [ ] Implement `generate` command - Generate new similar exercises

## Phase 5 - Quiz System
- [ ] Implement `quiz` command - Generate quizzes from exercises
- [ ] Spaced repetition algorithm (SM-2)
- [ ] Progress tracking and analytics

## Known Issues
- Groq free tier rate limit (30 req/min) prevents analyzing large courses in one run
- Splitter may over-split on some edge cases (needs more real-world testing)
- Topics can be duplicated with slight variations in naming
