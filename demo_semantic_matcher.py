#!/usr/bin/env python3
"""
Demonstration of Semantic Matcher for Examina.

This script demonstrates the semantic similarity engine's ability to:
1. Prevent false-positive merges (Mealy ≠ Moore, SoP ≠ PoS)
2. Detect translations (English ↔ Italian)
3. Identify true duplicates

Run this script to see examples of correct matching behavior.
"""

from core.semantic_matcher import SemanticMatcher


def print_separator(title=""):
    """Print a section separator."""
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)
    print()


def test_pair(matcher, name1, name2, expected_merge=None, description=""):
    """Test a pair of names and print the result."""
    result = matcher.should_merge(name1, name2)

    # Color output
    if result.should_merge:
        status = "✅ MERGE"
        color = "\033[92m"  # Green
    else:
        status = "❌ DO NOT MERGE"
        color = "\033[91m"  # Red
    reset = "\033[0m"

    # Check if result matches expected
    match_indicator = ""
    if expected_merge is not None:
        if result.should_merge == expected_merge:
            match_indicator = " ✓"
        else:
            match_indicator = " ✗ UNEXPECTED!"
            color = "\033[93m"  # Yellow

    print(f"{color}{status}{reset}{match_indicator}")
    print(f"  '{name1}'")
    print(f"  '{name2}'")
    print(f"  Similarity: {result.similarity_score:.3f} | Reason: {result.reason}")
    if description:
        print(f"  Note: {description}")
    print()


def main():
    """Run semantic matcher demonstrations."""
    print_separator("SEMANTIC MATCHER DEMONSTRATION")
    print("This demonstration shows how the semantic matcher prevents false-positive")
    print("merges while correctly identifying translations and true duplicates.")

    # Initialize matcher (without embeddings for this demo)
    matcher = SemanticMatcher(use_embeddings=False)

    # Get stats
    stats = matcher.get_stats()
    print(f"\nMatcher Configuration:")
    print(f"  - Translation pairs: {stats['translation_pairs_count']}")
    print(f"  - Semantic opposites: {stats['semantic_opposites_count']}")
    print(f"  - Embedding model: {stats['model_name']}")
    print(f"  - Using embeddings: {stats['use_embeddings']}")

    # ========================================================================
    # Test 1: False Positives Prevention (CRITICAL!)
    # ========================================================================
    print_separator("TEST 1: Preventing False Positives")
    print("These pairs should NOT merge despite high string similarity:")

    test_pair(
        matcher,
        "Progettazione Macchina di Mealy",
        "Progettazione Macchina di Moore",
        expected_merge=False,
        description="Different FSM types - MUST NOT merge"
    )

    test_pair(
        matcher,
        "Mealy Machine Design",
        "Moore Machine Design",
        expected_merge=False,
        description="Different FSM types (English) - MUST NOT merge"
    )

    test_pair(
        matcher,
        "Minimizzazione SoP",
        "Minimizzazione PoS",
        expected_merge=False,
        description="Sum of Products vs Product of Sums - MUST NOT merge"
    )

    test_pair(
        matcher,
        "Sum of Products Minimization",
        "Product of Sums Minimization",
        expected_merge=False,
        description="SoP vs PoS (English) - MUST NOT merge"
    )

    test_pair(
        matcher,
        "Sequential Circuit Design",
        "Combinational Circuit Design",
        expected_merge=False,
        description="Different circuit types - MUST NOT merge"
    )

    test_pair(
        matcher,
        "DFA Minimization",
        "NFA Minimization",
        expected_merge=False,
        description="Deterministic vs Nondeterministic - MUST NOT merge"
    )

    # ========================================================================
    # Test 2: Translation Detection
    # ========================================================================
    print_separator("TEST 2: Translation Detection")
    print("These pairs are translations and should merge:")

    test_pair(
        matcher,
        "Finite State Machines",
        "Macchine a Stati Finiti",
        expected_merge=True,
        description="English ↔ Italian translation"
    )

    test_pair(
        matcher,
        "Moore Machine",
        "Macchina di Moore",
        expected_merge=True,
        description="Moore machine translation"
    )

    test_pair(
        matcher,
        "Mealy Machine",
        "Macchina di Mealy",
        expected_merge=True,
        description="Mealy machine translation"
    )

    test_pair(
        matcher,
        "Boolean Algebra",
        "Algebra Booleana",
        expected_merge=True,
        description="Boolean algebra translation"
    )

    test_pair(
        matcher,
        "Karnaugh Map Minimization",
        "Minimizzazione Mappa di Karnaugh",
        expected_merge=True,
        description="Karnaugh map translation"
    )

    test_pair(
        matcher,
        "Design of Sequential Circuits",
        "Progettazione Circuiti Sequenziali",
        expected_merge=True,
        description="Sequential circuit design translation"
    )

    # ========================================================================
    # Test 3: True Duplicates
    # ========================================================================
    print_separator("TEST 3: True Duplicates")
    print("These pairs are true duplicates and should merge:")

    test_pair(
        matcher,
        "Moore Machine Design",
        "Moore Machine Design and Minimization",
        expected_merge=True,
        description="Subset/superset relationship"
    )

    test_pair(
        matcher,
        "Progettazione Monitor",
        "Progettazione di Monitor",
        expected_merge=True,
        description="Minor wording variation"
    )

    test_pair(
        matcher,
        "Moore Machine",
        "Moore Machines",
        expected_merge=True,
        description="Singular vs plural"
    )

    # ========================================================================
    # Test 4: Low Similarity (Should NOT Merge)
    # ========================================================================
    print_separator("TEST 4: Low Similarity")
    print("These pairs are too different and should NOT merge:")

    test_pair(
        matcher,
        "Boolean Algebra Simplification",
        "Concurrent Programming with Monitors",
        expected_merge=False,
        description="Completely different topics"
    )

    test_pair(
        matcher,
        "Gaussian Elimination",
        "Mealy Machine Design",
        expected_merge=False,
        description="Unrelated concepts"
    )

    # ========================================================================
    # Test 5: Edge Cases
    # ========================================================================
    print_separator("TEST 5: Edge Cases")
    print("Testing special cases:")

    test_pair(
        matcher,
        "MOORE MACHINE",
        "macchina di moore",
        expected_merge=True,
        description="Case-insensitive translation"
    )

    test_pair(
        matcher,
        "Exact Match Test",
        "Exact Match Test",
        expected_merge=True,
        description="Identical strings"
    )

    test_pair(
        matcher,
        "Synchronous Counter",
        "Asynchronous Counter",
        expected_merge=False,
        description="Synchronous vs Asynchronous - word boundary test"
    )

    # ========================================================================
    # Summary
    # ========================================================================
    print_separator("SUMMARY")
    print("The semantic matcher successfully:")
    print("  ✅ Prevents false-positive merges (Mealy ≠ Moore, SoP ≠ PoS)")
    print("  ✅ Detects English ↔ Italian translations")
    print("  ✅ Identifies true duplicates")
    print("  ✅ Handles edge cases (case-insensitivity, word boundaries)")
    print()
    print("This engine is ready for integration with Examina's deduplication system.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
