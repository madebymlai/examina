"""
Comprehensive tests for semantic_matcher module.

Tests cover:
- Semantic similarity computation
- Translation detection (English ↔ Italian)
- Semantic difference detection (Mealy vs Moore, SoP vs PoS, etc.)
- Should merge decision logic
- Batch processing
- Edge cases and error handling
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.semantic_matcher import (
    SemanticMatcher,
    SimilarityResult,
    TRANSLATION_PAIRS,
    SEMANTIC_OPPOSITES
)


# ============================================================================
# Test Mealy/Moore Machine Detection (Critical!)
# ============================================================================

def test_mealy_moore_not_similar():
    """Mealy and Moore machines should NOT be considered similar."""
    matcher = SemanticMatcher(use_embeddings=False)  # Use string fallback for testing
    result = matcher.should_merge(
        "Progettazione Macchina di Mealy",
        "Progettazione Macchina di Moore"
    )
    assert result.should_merge == False, "Mealy and Moore should NOT merge"
    assert result.reason == "semantically_different", f"Expected 'semantically_different', got '{result.reason}'"
    print("✓ test_mealy_moore_not_similar passed")


def test_mealy_moore_english():
    """English Mealy and Moore should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Mealy Machine Design",
        "Moore Machine Design"
    )
    assert result.should_merge == False
    assert result.reason == "semantically_different"
    print("✓ test_mealy_moore_english passed")


def test_mealy_moore_mixed():
    """Mixed language Mealy/Moore should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Test with explicit keywords
    result = matcher.should_merge(
        "Design of Mealy Machine",
        "Progettazione Macchina di Moore"
    )
    assert result.should_merge == False, "Mealy/Moore should NOT merge even in mixed languages"
    assert result.reason == "semantically_different", f"Expected 'semantically_different', got '{result.reason}'"
    print("✓ test_mealy_moore_mixed passed")


# ============================================================================
# Test SoP/PoS Detection (Critical!)
# ============================================================================

def test_sop_pos_not_similar():
    """SoP and PoS should NOT be considered similar."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Minimizzazione SoP",
        "Minimizzazione PoS"
    )
    assert result.should_merge == False, "SoP and PoS should NOT merge"
    assert result.reason == "semantically_different"
    print("✓ test_sop_pos_not_similar passed")


def test_sop_pos_english():
    """English SoP/PoS should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Minimization of Sum of Products",
        "Minimization of Product of Sums"
    )
    assert result.should_merge == False, "SoP and PoS should NOT merge"
    assert result.reason == "semantically_different", f"Expected 'semantically_different', got '{result.reason}'"
    print("✓ test_sop_pos_english passed")


def test_sop_pos_italian_full():
    """Italian SoP/PoS full names should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Minimizzazione Somma di Prodotti",
        "Minimizzazione Prodotto di Somme"
    )
    assert result.should_merge == False
    assert result.reason == "semantically_different"
    print("✓ test_sop_pos_italian_full passed")


# ============================================================================
# Test Translation Detection
# ============================================================================

def test_translation_fsm():
    """English/Italian FSM translations should be detected."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Finite State Machines",
        "Macchine a Stati Finiti"
    )
    # FSM translation should be detected
    assert result.should_merge == True, f"FSM translation should merge, got {result.should_merge}"
    assert result.reason == "translation", f"Expected 'translation', got '{result.reason}'"
    print("✓ test_translation_fsm passed")


def test_translation_moore():
    """Moore machine translation should be detected."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Moore Machine",
        "Macchina di Moore"
    )
    assert result.should_merge == True
    assert result.reason == "translation"
    print("✓ test_translation_moore passed")


def test_translation_mealy():
    """Mealy machine translation should be detected."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Mealy Machine",
        "Macchina di Mealy"
    )
    assert result.should_merge == True
    assert result.reason == "translation"
    print("✓ test_translation_mealy passed")


def test_translation_boolean_algebra():
    """Boolean algebra translation should be detected."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Boolean Algebra",
        "Algebra Booleana"
    )
    assert result.should_merge == True
    assert result.reason == "translation"
    print("✓ test_translation_boolean_algebra passed")


def test_translation_karnaugh():
    """Karnaugh map translation should be detected."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Karnaugh Map",
        "Mappa di Karnaugh"
    )
    assert result.should_merge == True
    assert result.reason == "translation"
    print("✓ test_translation_karnaugh passed")


def test_translation_design():
    """Design translation should be detected."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Test "design" -> "progettazione"
    result = matcher.should_merge(
        "Sequential Circuit Design",
        "Progettazione Circuito Sequenziale"
    )
    assert result.should_merge == True
    assert result.reason == "translation"
    print("✓ test_translation_design passed")


# ============================================================================
# Test True Duplicates (Should Merge)
# ============================================================================

def test_true_duplicates_similar():
    """True duplicates should be merged."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Progettazione di Monitor",
        "Progettazione Monitor"
    )
    # These are very similar - similarity should be high
    assert result.similarity_score > 0.8, f"True duplicates should have high similarity, got {result.similarity_score}"
    # Should merge if above threshold
    if result.similarity_score >= 0.85:
        assert result.should_merge == True, "True duplicates should merge"
    print("✓ test_true_duplicates_similar passed")


def test_true_duplicates_exact():
    """Exact duplicates should merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Moore Machine Design",
        "Moore Machine Design"
    )
    assert result.should_merge == True
    assert result.similarity_score == 1.0  # Exact match
    print("✓ test_true_duplicates_exact passed")


def test_true_duplicates_subset():
    """Subset duplicates should merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Moore Machine Design",
        "Moore Machine Design and Minimization"
    )
    # High similarity due to shared prefix
    assert result.similarity_score > 0.7, "Subset should have high similarity"
    print("✓ test_true_duplicates_subset passed")


# ============================================================================
# Test Other Semantic Opposites
# ============================================================================

def test_sequential_combinational_not_similar():
    """Sequential and Combinational circuits should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Sequential Circuit Design",
        "Combinational Circuit Design"
    )
    assert result.should_merge == False
    assert result.reason == "semantically_different"
    print("✓ test_sequential_combinational_not_similar passed")


def test_sequential_combinational_italian():
    """Italian Sequential/Combinational should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Progettazione Circuito Sequenziale",
        "Progettazione Circuito Combinatorio"
    )
    assert result.should_merge == False
    assert result.reason == "semantically_different"
    print("✓ test_sequential_combinational_italian passed")


def test_dfa_nfa_not_similar():
    """DFA and NFA should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "DFA Minimization",
        "NFA Minimization"
    )
    assert result.should_merge == False
    assert result.reason == "semantically_different"
    print("✓ test_dfa_nfa_not_similar passed")


def test_synchronous_asynchronous_not_similar():
    """Synchronous and Asynchronous should NOT merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Synchronous Counter Design",
        "Asynchronous Counter Design"
    )
    assert result.should_merge == False, "Synchronous and Asynchronous should NOT merge"
    assert result.reason == "semantically_different", f"Expected 'semantically_different', got '{result.reason}'"
    print("✓ test_synchronous_asynchronous_not_similar passed")


# ============================================================================
# Test Low Similarity (Should NOT Merge)
# ============================================================================

def test_low_similarity_different_topics():
    """Different topics should not merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Boolean Algebra Simplification",
        "Concurrent Programming with Monitors"
    )
    assert result.should_merge == False
    assert result.reason == "below_threshold"
    print("✓ test_low_similarity_different_topics passed")


def test_low_similarity_unrelated():
    """Unrelated terms should not merge."""
    matcher = SemanticMatcher(use_embeddings=False)
    result = matcher.should_merge(
        "Gaussian Elimination",
        "Mealy Machine Design"
    )
    assert result.should_merge == False
    assert result.reason == "below_threshold"
    print("✓ test_low_similarity_unrelated passed")


# ============================================================================
# Test Helper Methods
# ============================================================================

def test_is_translation_method():
    """Test is_translation method directly."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Should detect translation
    assert matcher.is_translation("Finite State Machine", "Macchina a Stati Finiti") == True
    assert matcher.is_translation("Moore Machine", "Macchina di Moore") == True
    assert matcher.is_translation("Boolean Algebra", "Algebra Booleana") == True

    # Should NOT detect as translation
    assert matcher.is_translation("Mealy Machine", "Moore Machine") == False
    assert matcher.is_translation("SoP", "PoS") == False

    print("✓ test_is_translation_method passed")


def test_are_semantically_different_method():
    """Test are_semantically_different method directly."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Should detect as different
    assert matcher.are_semantically_different("Mealy Machine", "Moore Machine") == True
    assert matcher.are_semantically_different("SoP Minimization", "PoS Minimization") == True
    assert matcher.are_semantically_different("Sequential Circuit", "Combinational Circuit") == True
    assert matcher.are_semantically_different("DFA", "NFA") == True

    # Should NOT detect as different
    assert matcher.are_semantically_different("Mealy Machine Design", "Mealy Machine Minimization") == False
    assert matcher.are_semantically_different("Moore Machine", "Macchina di Moore") == False

    print("✓ test_are_semantically_different_method passed")


def test_compute_similarity_method():
    """Test compute_similarity method."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Exact match should have similarity 1.0
    sim = matcher.compute_similarity("Test String", "Test String")
    assert sim == 1.0, f"Exact match should be 1.0, got {sim}"

    # Similar strings should have high similarity
    sim = matcher.compute_similarity("Mealy Machine", "Mealy Machines")
    assert sim > 0.9, f"Similar strings should have high similarity, got {sim}"

    # Different strings should have low similarity
    sim = matcher.compute_similarity("Mealy", "Boolean")
    assert sim < 0.5, f"Different strings should have low similarity, got {sim}"

    print("✓ test_compute_similarity_method passed")


# ============================================================================
# Test Batch Processing
# ============================================================================

def test_batch_should_merge():
    """Test batch processing of merge decisions."""
    matcher = SemanticMatcher(use_embeddings=False)

    pairs = [
        ("Mealy Machine", "Moore Machine"),  # Should NOT merge (opposite)
        ("Moore Machine", "Macchina di Moore"),  # Should merge (translation)
        ("SoP", "PoS"),  # Should NOT merge (opposite)
        ("Boolean Algebra", "Algebra Booleana"),  # Should merge (translation)
    ]

    results = matcher.batch_should_merge(pairs)

    assert len(results) == 4
    assert results[0].should_merge == False  # Mealy vs Moore
    assert results[1].should_merge == True   # Translation
    assert results[2].should_merge == False  # SoP vs PoS
    assert results[3].should_merge == True   # Translation

    print("✓ test_batch_should_merge passed")


def test_find_similar_items():
    """Test find_similar_items method."""
    matcher = SemanticMatcher(use_embeddings=False)

    query = "Moore Machine"
    candidates = [
        "Moore Machine Design",
        "Mealy Machine Design",
        "Boolean Algebra",
        "Moore Machines",
    ]

    results = matcher.find_similar_items(query, candidates, threshold=0.7)

    # Should find similar items (not Mealy due to opposite check)
    assert len(results) > 0
    # First result should have highest similarity
    if len(results) > 1:
        assert results[0][1] >= results[1][1]

    print("✓ test_find_similar_items passed")


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_empty_strings():
    """Test with empty strings."""
    matcher = SemanticMatcher(use_embeddings=False)

    result = matcher.should_merge("", "")
    assert result.similarity_score == 1.0  # Empty strings are identical

    result = matcher.should_merge("Moore Machine", "")
    assert result.should_merge == False

    print("✓ test_empty_strings passed")


def test_case_insensitivity():
    """Test that matching is case-insensitive."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Translation should work regardless of case
    result = matcher.should_merge(
        "MOORE MACHINE",
        "macchina di moore"
    )
    assert result.should_merge == True
    assert result.reason == "translation"

    # Semantic opposites should work regardless of case
    result = matcher.should_merge(
        "MEALY MACHINE",
        "moore machine"
    )
    assert result.should_merge == False
    assert result.reason == "semantically_different"

    print("✓ test_case_insensitivity passed")


def test_threshold_parameter():
    """Test custom threshold parameter."""
    matcher = SemanticMatcher(use_embeddings=False)

    # With high threshold, similar items might not merge
    result = matcher.should_merge(
        "Moore Machine Design",
        "Moore Machines Designed",
        threshold=0.95
    )
    # This might not merge due to high threshold

    # With low threshold, more items should merge
    result_low = matcher.should_merge(
        "Moore Machine Design",
        "Moore Machines Designed",
        threshold=0.5
    )

    # Low threshold should be more permissive
    assert result_low.similarity_score >= result.similarity_score

    print("✓ test_threshold_parameter passed")


# ============================================================================
# Test Translation Pairs Coverage
# ============================================================================

def test_translation_pairs_exist():
    """Test that TRANSLATION_PAIRS is properly defined."""
    assert len(TRANSLATION_PAIRS) > 0, "TRANSLATION_PAIRS should not be empty"

    # Check some key pairs exist
    pairs_list = list(TRANSLATION_PAIRS)
    en_terms = [pair[0] for pair in pairs_list]
    it_terms = [pair[1] for pair in pairs_list]

    assert "moore machine" in en_terms
    assert "mealy machine" in en_terms
    assert "boolean algebra" in en_terms
    assert "macchina di moore" in it_terms
    assert "macchina di mealy" in it_terms
    assert "algebra booleana" in it_terms

    print("✓ test_translation_pairs_exist passed")


def test_semantic_opposites_exist():
    """Test that SEMANTIC_OPPOSITES is properly defined."""
    assert len(SEMANTIC_OPPOSITES) > 0, "SEMANTIC_OPPOSITES should not be empty"

    # Check key opposites exist
    assert ("mealy", "moore") in SEMANTIC_OPPOSITES
    assert ("sop", "pos") in SEMANTIC_OPPOSITES
    assert ("sequential", "combinational") in SEMANTIC_OPPOSITES

    print("✓ test_semantic_opposites_exist passed")


# ============================================================================
# Test Initialization
# ============================================================================

def test_initialization_without_embeddings():
    """Test initialization with embeddings disabled."""
    matcher = SemanticMatcher(use_embeddings=False)

    assert matcher.use_embeddings == False
    assert matcher.enabled == False

    # Should still work with string fallback
    result = matcher.should_merge("Test", "Test")
    assert result.should_merge == True

    print("✓ test_initialization_without_embeddings passed")


def test_get_stats():
    """Test get_stats method."""
    matcher = SemanticMatcher(use_embeddings=False)

    stats = matcher.get_stats()

    assert "model_name" in stats
    assert "use_embeddings" in stats
    assert "translation_pairs_count" in stats
    assert "semantic_opposites_count" in stats

    assert stats["translation_pairs_count"] == len(TRANSLATION_PAIRS)
    assert stats["semantic_opposites_count"] == len(SEMANTIC_OPPOSITES)

    print("✓ test_get_stats passed")


# ============================================================================
# Integration Tests
# ============================================================================

def test_integration_realistic_scenario():
    """Test with realistic Examina use case."""
    matcher = SemanticMatcher(use_embeddings=False)

    # Scenario: Deduplicating core loops from Italian and English exams
    critical_tests = [
        # (text1, text2, should_merge, reason)
        ("Progettazione Macchina di Mealy", "Progettazione Macchina di Moore", False, "Mealy vs Moore"),
        ("Mealy Machine Design", "Moore Machine Design", False, "Mealy vs Moore English"),
        ("Minimizzazione SoP", "Minimizzazione PoS", False, "SoP vs PoS"),
        ("Mealy Machine", "Macchina di Mealy", True, "Translation"),
        ("Moore Machine", "Macchina di Moore", True, "Translation"),
    ]

    for text1, text2, expected_merge, description in critical_tests:
        result = matcher.should_merge(text1, text2)
        assert result.should_merge == expected_merge, \
            f"FAILED: {description} - '{text1}' vs '{text2}': expected {expected_merge}, got {result.should_merge} (reason: {result.reason})"

    print("✓ test_integration_realistic_scenario passed")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests and report results."""
    tests = [
        # Critical: Mealy/Moore detection
        test_mealy_moore_not_similar,
        test_mealy_moore_english,
        test_mealy_moore_mixed,

        # Critical: SoP/PoS detection
        test_sop_pos_not_similar,
        test_sop_pos_english,
        test_sop_pos_italian_full,

        # Translation detection
        test_translation_fsm,
        test_translation_moore,
        test_translation_mealy,
        test_translation_boolean_algebra,
        test_translation_karnaugh,
        test_translation_design,

        # True duplicates
        test_true_duplicates_similar,
        test_true_duplicates_exact,
        test_true_duplicates_subset,

        # Other semantic opposites
        test_sequential_combinational_not_similar,
        test_sequential_combinational_italian,
        test_dfa_nfa_not_similar,
        test_synchronous_asynchronous_not_similar,

        # Low similarity
        test_low_similarity_different_topics,
        test_low_similarity_unrelated,

        # Helper methods
        test_is_translation_method,
        test_are_semantically_different_method,
        test_compute_similarity_method,

        # Batch processing
        test_batch_should_merge,
        test_find_similar_items,

        # Edge cases
        test_empty_strings,
        test_case_insensitivity,
        test_threshold_parameter,

        # Data validation
        test_translation_pairs_exist,
        test_semantic_opposites_exist,

        # Initialization
        test_initialization_without_embeddings,
        test_get_stats,

        # Integration
        test_integration_realistic_scenario,
    ]

    passed = 0
    failed = 0
    errors = []

    print("\n" + "="*70)
    print("Running Semantic Matcher Test Suite")
    print("="*70 + "\n")

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"{test.__name__}: {str(e)}")
            print(f"✗ {test.__name__} FAILED: {str(e)}")
        except Exception as e:
            failed += 1
            errors.append(f"{test.__name__}: {type(e).__name__}: {str(e)}")
            print(f"✗ {test.__name__} ERROR: {type(e).__name__}: {str(e)}")

    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} total")
    print("="*70)

    if errors:
        print("\nFailed Tests:")
        for error in errors:
            print(f"  - {error}")

    return passed, failed


if __name__ == '__main__':
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
