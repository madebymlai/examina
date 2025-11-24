# Examina - TODO

## Active Development

### Phase 7 - Enhanced Learning System ✅ COMPLETED

**Core Features:**
- ✅ Deep theory explanations with prerequisite concepts
- ✅ Step-by-step reasoning with WHY for each step
- ✅ Three depth levels (basic, medium, advanced)
- ✅ Metacognitive learning strategies module (`core/metacognitive.py`)
- ✅ Study tips per topic/difficulty (context-aware, research-backed)
- ✅ Problem-solving frameworks (Polya, IDEAL, Feynman, Rubber Duck)
- ✅ Self-assessment prompts (Bloom's taxonomy)
- ✅ Retrieval practice suggestions (5 techniques)
- ✅ Interactive proof practice mode (`prove` command)

**Future Enhancements:**
- [ ] Integrate metacognitive tips into `learn` command UI
- [ ] Adaptive teaching based on mastery level
- [ ] Track student understanding per topic
- [ ] Detect knowledge gaps and fill proactively
- [ ] Personalized learning paths

## High Priority Improvements

### Phase 3 - AI Analysis
- [ ] **Handle exam files with solutions** - Parse PDFs that include both questions AND solutions in the same document (currently assumes questions-only format)
- [ ] Provider-agnostic rate limiting tracker

### Phase 6 - Multi-Core-Loop Support
- [x] **Clean up orphaned core loops** - ✅ Added `--clean-orphans` flag to deduplicate command
- [ ] **Fix mis-categorized exercises** - Re-analyze courses to fix LLM analysis errors (e.g., Mealy exercises linked to Moore core loops)
- [ ] Bilingual procedure deduplication - Merge duplicate procedures across languages
- [ ] Strictly monolingual analysis mode - Ensure procedures extracted in only one language
- [ ] Cross-language procedure similarity - Use embeddings to match equivalent procedures

### Phase 9 - Theory & Proof Support
- [ ] Re-analyze existing 75 exercises with Phase 9 detection
- [ ] Tune theory detection threshold (2 keywords → 1 keyword)
- [ ] Add interactive proof practice mode
- [ ] Build theory concept dependency visualization

## Low Priority / Future

- [ ] Language detection for procedures - Automatically detect and merge equivalent procedures
- [ ] Concept normalization - Handle variations like "autovalori_autovettori" vs "autovalori_e_autovettori"
- [ ] Interactive merge review for deduplication - Manual approve/reject
- [ ] Merge history tracking - Allow undo operations
- [ ] Core loop similarity tuning - Review 95 ADE merges (might be legitimate)

## Known Issues

- **Groq rate limit**: Free tier (30 req/min) prevents analyzing large courses in one run
- **API timeouts**: Enhanced learn with prerequisites may timeout - use `--no-concepts` flag
- **Topic splitting**: `--delete-old` may fail due to foreign key constraints if topic has references

## Notes

For completed phases and detailed implementation history, see [CHANGELOG.md](CHANGELOG.md).
