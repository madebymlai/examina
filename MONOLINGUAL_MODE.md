# Monolingual Analysis Mode (Phase 6 TODO)

## Overview

Strictly monolingual analysis mode ensures that all procedures extracted during analysis are in **only one language**, preventing future cross-language duplicates.

This feature addresses the problem of bilingual courses where exercises might be in multiple languages (e.g., Italian and English), leading to duplicate procedures like:
- "Calcolo Autovalori" (Italian)
- "Eigenvalue Calculation" (English)

With monolingual mode enabled, both will be normalized to a single language based on the detected primary course language.

## Features

1. **Primary Language Detection**: Automatically detects the primary language of a course by analyzing the first few exercises
2. **Procedure Translation**: Translates procedures from non-primary languages to the primary language using LLM
3. **Cross-Language Deduplication**: Prevents duplicate procedures in different languages
4. **Graceful Fallback**: If language detection or translation fails, falls back to bilingual mode

## Usage

### Command Line

```bash
# Analyze course with monolingual mode enabled
python cli.py analyze --course <course_code> --monolingual

# Example with other options
python cli.py analyze --course B006802 --monolingual --lang en --provider anthropic
```

### Configuration

You can set the default mode via environment variable:

```bash
# Enable monolingual mode by default
export EXAMINA_MONOLINGUAL_ENABLED=true

# Disable monolingual mode (default - bilingual)
export EXAMINA_MONOLINGUAL_ENABLED=false
```

## How It Works

### 1. Primary Language Detection

When analysis starts with `--monolingual` flag:

```python
# Samples first 5 exercises
# Detects language of each using LLM
# Selects most common language as primary
primary_language = analyzer._detect_primary_language(exercises, course_name)
```

Example output:
```
[INFO] Detected primary course language: italian (from 5 exercises)
[MONOLINGUAL MODE] Primary language set to: italian
  All procedures will be normalized to italian
```

### 2. Procedure Extraction and Normalization

For each exercise analyzed:

```python
# Extract procedures (may be in any language)
procedures = extract_procedures_from_llm_response(...)

# Normalize to primary language if monolingual mode
if monolingual:
    procedures = normalize_procedures_to_primary_language(procedures)
```

### 3. Translation Process

For each procedure in non-primary language:

```python
# Detect procedure language
proc_lang = translation_detector.detect_language(procedure.name)

# If different from primary, translate
if proc_lang != primary_language:
    translated = llm.translate(procedure, target_language=primary_language)
```

Example:
```
[MONOLINGUAL] Translating procedure 'Eigenvalue Calculation' from english to italian
  → 'Calcolo degli Autovalori'
```

### 4. Database Storage

All procedures are stored with language metadata:

```sql
INSERT INTO core_loops (id, name, language, ...)
VALUES ('calcolo_autovalori', 'Calcolo degli Autovalori', 'italian', ...)
```

## Architecture

### Modified Files

1. **cli.py**
   - Added `--monolingual` flag to `analyze` command
   - Passes flag to `ExerciseAnalyzer` constructor
   - Uses primary language for database storage

2. **config.py**
   - Added `MONOLINGUAL_MODE_ENABLED` config option
   - Default: `false` (bilingual mode for backward compatibility)

3. **core/analyzer.py**
   - Added `monolingual` parameter to constructor
   - Implemented `_detect_primary_language()` method
   - Implemented `_translate_procedure()` method
   - Implemented `_normalize_procedures_to_primary_language()` method
   - Integrated normalization into `analyze_exercise()` flow

### Key Methods

#### `_detect_primary_language(exercises, course_name)`
Detects primary language from course exercises.

**Args:**
- `exercises`: List of exercise dicts
- `course_name`: Course name for context

**Returns:**
- Primary language code (e.g., "english", "italian")

**Algorithm:**
1. Sample first 5 exercises
2. Detect language of each using `TranslationDetector.detect_language()`
3. Count occurrences of each language
4. Return most common language
5. Fallback to analysis language if detection fails

#### `_translate_procedure(procedure_info, target_language)`
Translates a procedure to target language using LLM.

**Args:**
- `procedure_info`: ProcedureInfo to translate
- `target_language`: Target language (e.g., "english")

**Returns:**
- Translated ProcedureInfo

**Process:**
1. Build translation prompt with procedure name and steps
2. Call LLM with `json_mode=True`
3. Parse translated name and steps
4. Return new ProcedureInfo with translated content
5. Fallback to original if translation fails

#### `_normalize_procedures_to_primary_language(procedures)`
Normalizes all procedures to primary language.

**Args:**
- `procedures`: List of ProcedureInfo objects

**Returns:**
- List of normalized ProcedureInfo objects

**Logic:**
1. If not in monolingual mode, return unchanged
2. For each procedure:
   - Detect its language
   - If matches primary language, keep as is
   - If different, translate to primary language
3. Return list of normalized procedures

## Benefits

### Before Monolingual Mode (Bilingual)

```
Topics: Autovalori e Diagonalizzazione
  Core Loops:
    - calcolo_autovalori (Italian)
    - eigenvalue_calculation (English)  ← DUPLICATE!
    - diagonalizzazione_matrici (Italian)
    - matrix_diagonalization (English)  ← DUPLICATE!
```

### After Monolingual Mode (Italian)

```
Topics: Autovalori e Diagonalizzazione
  Core Loops:
    - calcolo_autovalori (Italian)
    - diagonalizzazione_matrici (Italian)
```

### After Monolingual Mode (English)

```
Topics: Eigenvalues and Diagonalization
  Core Loops:
    - eigenvalue_calculation (English)
    - matrix_diagonalization (English)
```

## Design Decisions

### Why Default to OFF?

Monolingual mode is **disabled by default** for backward compatibility:

1. **Existing Courses**: Bilingual courses should continue working
2. **User Choice**: Users explicitly opt-in with `--monolingual` flag
3. **Translation Costs**: LLM translation adds API calls and latency
4. **Language Mixing**: Some courses intentionally use multiple languages

### Why Use LLM Translation?

Alternatives considered:

1. ❌ **Dictionary-based translation**: Limited, doesn't handle technical terms
2. ❌ **Embedding-only detection**: Can't translate, only detect similarity
3. ✅ **LLM-based translation**: Handles technical terms, context-aware, high quality

### Graceful Degradation

If translation fails:
- Keep original procedure (don't lose data)
- Log warning for debugging
- Continue analysis (don't block entire process)

## Testing

Run the test suite:

```bash
python test_monolingual.py
```

Tests cover:
1. Primary language detection
2. Procedure translation
3. Monolingual normalization
4. Bilingual mode (disabled)

## Examples

### Example 1: Italian Course

```bash
python cli.py analyze --course ALGEBRA_LINEARE --monolingual
```

Output:
```
[INFO] Detected primary course language: italian (from 5 exercises)
[MONOLINGUAL MODE] Primary language set to: italian
  All procedures will be normalized to italian

[MONOLINGUAL] Translating procedure 'Eigenvalue Calculation' from english to italian
  → 'Calcolo degli Autovalori'

[MONOLINGUAL] Translating procedure 'Matrix Diagonalization' from english to italian
  → 'Diagonalizzazione di Matrici'

✓ Merged 47 fragments → 23 exercises

📚 Discovered Topics:
  • Autovalori e Diagonalizzazione (8 exercises, 2 core loops)

🔄 Discovered Core Loops:
  • Calcolo degli Autovalori (5 exercises)
  • Diagonalizzazione di Matrici (3 exercises)
```

### Example 2: English Course

```bash
python cli.py analyze --course LINEAR_ALGEBRA --monolingual --lang en
```

Output:
```
[INFO] Detected primary course language: english (from 5 exercises)
[MONOLINGUAL MODE] Primary language set to: english
  All procedures will be normalized to english

[MONOLINGUAL] Translating procedure 'Calcolo Autovalori' from italian to english
  → 'Eigenvalue Calculation'

✓ Merged 47 fragments → 23 exercises

📚 Discovered Topics:
  • Eigenvalues and Diagonalization (8 exercises, 2 core loops)
```

## Limitations

1. **LLM Dependency**: Requires working LLM provider for translation
2. **API Costs**: Each translation adds LLM API calls
3. **Translation Quality**: Depends on LLM accuracy
4. **Language Detection**: May fail on very short or ambiguous text
5. **Mixed Language Exercises**: Single exercise with multiple languages is normalized to primary

## Future Enhancements

Potential improvements:

1. **Translation Caching**: Cache translations to reduce API calls
2. **Batch Translation**: Translate multiple procedures in one call
3. **User Language Preference**: Allow user to specify preferred language
4. **Hybrid Mode**: Keep both languages but link as translations
5. **Translation Confidence**: Validate translation quality before accepting

## Related Features

- **Phase 6: Language Detection** - Automatic language detection system
- **Translation Detection** - Generic bilingual deduplication
- **Semantic Matching** - Cross-language similarity detection

## Troubleshooting

### Translation not working

**Problem**: Procedures not being translated

**Solutions**:
1. Check LLM provider is configured (API key set)
2. Verify `--monolingual` flag is passed
3. Check logs for translation errors
4. Ensure `TranslationDetector` initialized successfully

### Wrong primary language detected

**Problem**: Primary language detected incorrectly

**Solutions**:
1. Check first 5 exercises are representative
2. Manually verify exercise language
3. Use `--lang` flag to hint expected language
4. Check LLM language detection is working

### Performance issues

**Problem**: Analysis is very slow

**Solutions**:
1. Translation adds ~1-2s per procedure
2. Use faster LLM model (e.g., `llama3.1:8b`)
3. Consider disabling monolingual mode for large courses
4. Use `--parallel` mode for better throughput

## Conclusion

Monolingual analysis mode provides a robust solution for preventing cross-language duplicates while maintaining backward compatibility with existing bilingual courses. The LLM-based translation approach ensures high-quality normalization while gracefully handling edge cases.
