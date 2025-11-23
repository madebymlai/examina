# Examina - TODO List

## Phase 3 - AI Analysis ✅ COMPLETED

**Done:**
- ✅ Intelligent splitter (filters instructions, works for all formats)
- ✅ AI analysis with Groq
- ✅ Rate limit handling with exponential retry
- ✅ Database + Vector store
- ✅ Topic and core loop discovery

**Future improvements (low priority):**
- [x] Topic/core loop deduplication - Automatic similarity-based merging (0.85 threshold)
- [x] Confidence threshold filtering - Filter low-confidence analyses (default 0.5)
- [x] Resume failed analysis - Checkpoint system with --force flag
- [x] Batch processing optimization - 7-8x speedup with parallel processing
- [x] Caching LLM responses - File-based cache with TTL, 100% hit rate on re-runs
- [ ] Provider-agnostic rate limiting tracker

## Phase 4 - Tutor Features ✅ COMPLETED

**Done:**
- ✅ **Add Anthropic Claude Sonnet 4.5** - Better rate limits, higher quality (14 topics, 23 core loops found!)
- ✅ **Analyze with Anthropic** - Successfully analyzed all 27 ADE exercises including SR Latch
- ✅ **Language switch (Italian/English)** - Added `--lang` flag to all commands (analyze, learn, practice, generate)
- ✅ **Tutor class** - Created core/tutor.py with learning, practice, and generation features
- ✅ **Learn command** - Explains core loops with theory, procedure, examples, and tips
- ✅ **Practice command** - Interactive practice with AI feedback and hints
- ✅ **Generate command** - Creates new exercise variations based on examples

**Tested:**
- All commands work with both English and Italian
- Learn: Generated comprehensive Moore machine tutorial
- Generate: Created new garage door control exercise
- Practice: Interactive answer evaluation with helpful feedback

## Phase 5 - Quiz System (NEXT)

**See PHASE_5_PLAN.md for detailed implementation plan**

### 5.1 Database Schema (2-3 hours)
- [ ] Add `quiz_sessions` table - Session metadata and scores
- [ ] Add `quiz_attempts` table - Individual question attempts
- [ ] Add `exercise_reviews` table - SM-2 spaced repetition data
- [ ] Add `topic_mastery` table - Aggregated mastery per topic
- [ ] Implement database migrations

### 5.2 SM-2 Algorithm (3-4 hours)
- [ ] Create `core/sm2.py` with SM-2 implementation
- [ ] Implement quality scoring (0-5 based on performance)
- [ ] Implement interval calculation (1d → 6d → EF-based)
- [ ] Implement easiness factor adjustment
- [ ] Implement mastery level progression (new → learning → reviewing → mastered)
- [ ] Add methods: `get_due_exercises()`, `update_mastery_level()`

### 5.3 Quiz Session Management (4-5 hours)
- [ ] Create `core/quiz.py` with QuizManager class
- [ ] Implement `create_quiz()` - Support random, topic, core_loop, review types
- [ ] Implement `get_next_question()` - Smart question selection
- [ ] Implement `submit_answer()` - Answer evaluation + SM-2 update
- [ ] Implement `complete_quiz()` - Final scoring and mastery updates
- [ ] Integrate with Tutor class for AI feedback

### 5.4 CLI Commands (5-6 hours)
- [ ] Implement `examina quiz` command with filters (topic, difficulty, core_loop)
- [ ] Add `--review-only` flag for spaced repetition mode
- [ ] Add `--questions N` flag for custom quiz length
- [ ] Implement interactive quiz flow with progress display
- [ ] Implement `examina progress` command with breakdowns
- [ ] Implement `examina suggest` command for study recommendations
- [ ] Add `--lang` support for all quiz commands

### 5.5 Progress Tracking & Analytics (4-5 hours)
- [ ] Create `core/analytics.py` with ProgressAnalytics class
- [ ] Implement `get_course_summary()` - Overall progress stats
- [ ] Implement `get_topic_breakdown()` - Per-topic mastery
- [ ] Implement `get_weak_areas()` - Identify struggling topics
- [ ] Implement `get_due_reviews()` - SM-2 scheduled reviews
- [ ] Implement `get_study_suggestions()` - Personalized recommendations
- [ ] Add Rich-based progress visualizations (bars, charts)

### 5.6 Testing (4-5 hours)
- [ ] Unit tests for SM-2 algorithm
- [ ] Unit tests for QuizManager
- [ ] Unit tests for Analytics
- [ ] Integration tests (full quiz flow)
- [ ] Real-world testing with ADE, AL, PC courses
- [ ] Test multi-language support

### Documentation
- [ ] Create `QUIZ_SYSTEM.md` - User guide
- [ ] Create `SM2_ALGORITHM.md` - Technical explanation
- [ ] Update `README.md` with Phase 5 features
- [ ] Add quiz examples to README

**Estimated Total Effort:** 35-45 hours (1-2 weeks)

## Known Issues
- Groq free tier rate limit (30 req/min) prevents analyzing large courses in one run
- Splitter may over-split on some edge cases (needs more real-world testing)
- Topics can be duplicated with slight variations in naming
