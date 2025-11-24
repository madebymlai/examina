#!/usr/bin/env python3
"""Test dynamic opposite detection with LLM."""

from core.semantic_matcher import SemanticMatcher
from models.llm_manager import LLMManager
from config import Config

# Create LLM manager
llm_manager = LLMManager(provider=Config.LLM_PROVIDER)

# Create semantic matcher with LLM
matcher = SemanticMatcher(llm_manager=llm_manager)

# Test cases that should NOT merge (opposites)
opposite_pairs = [
    ("sum of products", "product of sums"),
    ("SoP Minimization", "PoS Minimization"),
    ("NFA Design", "DFA Design"),
    ("Mealy Machine Design", "Moore Machine Design"),
    ("endothermic reaction", "exothermic reaction"),  # Chemistry domain
    ("positive charge", "negative charge"),  # Physics domain
]

# Test cases that SHOULD merge (translations/synonyms)
merge_pairs = [
    ("finite state machine", "macchina a stati finiti"),
    ("FSM minimization", "FSM minimizzazione"),
    ("boolean algebra", "algebra booleana"),
]

print("Testing Dynamic Opposite Detection\n")
print("=" * 60)

print("\n1. Testing pairs that should NOT merge (opposites):\n")
for text1, text2 in opposite_pairs:
    result = matcher.should_merge(text1, text2, threshold=0.85)
    status = "✓ CORRECT" if not result.should_merge else "✗ WRONG (merged)"
    print(f"{status}")
    print(f"  '{text1}' ↔ '{text2}'")
    print(f"  Similarity: {result.similarity_score:.2f}, Reason: {result.reason}")
    print()

print("\n2. Testing pairs that SHOULD merge (translations/synonyms):\n")
for text1, text2 in merge_pairs:
    result = matcher.should_merge(text1, text2, threshold=0.85)
    status = "✓ CORRECT" if result.should_merge else "✗ WRONG (didn't merge)"
    print(f"{status}")
    print(f"  '{text1}' ↔ '{text2}'")
    print(f"  Similarity: {result.similarity_score:.2f}, Reason: {result.reason}")
    print()

print("=" * 60)
print(f"\nCache statistics:")
print(f"  Opposite cache size: {len(matcher._opposite_cache)}")
