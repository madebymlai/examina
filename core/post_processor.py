"""
Post-processor for knowledge item validation.

Uses LLM to validate extracted items via coherence-based filtering.
Also detects synonyms for deduplication.
"""
import json
import logging
from typing import Any

from models.llm_manager import LLMManager

logger = logging.getLogger(__name__)


def detect_synonyms(
    items: list[tuple[str, str]],
    llm: LLMManager,
) -> list[tuple[str, str, list[str]]]:
    """
    Use LLM to detect synonym groups among knowledge items.

    Only groups items of the SAME type together. Different types = different skills.

    Args:
        items: List of (name, knowledge_type) tuples
        llm: LLMManager instance

    Returns:
        List of (canonical_name, type, member_names) tuples
        Example: [("moore_machine_design", "procedure", ["macchina_di_moore", "moore_design"])]
    """
    if len(items) < 2:
        return []

    # Group by type - only same-type items can be synonyms
    by_type: dict[str, list[str]] = {}
    for name, item_type in items:
        if item_type not in by_type:
            by_type[item_type] = []
        by_type[item_type].append(name)

    all_groups: list[tuple[str, str, list[str]]] = []

    # Run synonym detection per type
    for item_type, names in by_type.items():
        unique_names = list(set(names))
        if len(unique_names) < 2:
            continue

        prompt = f"""Identify knowledge item groups that should be MERGED into a single concept.

Names (snake_case - treat underscores as spaces):
{chr(10).join(f"- {name}" for name in unique_names)}

MERGE when items represent the SAME underlying skill or concept:
- A student who masters one item automatically masters the others
- A textbook would cover them in a single section, not separate chapters
- The difference is just naming/phrasing, not conceptual
- Items differ only by the specific instance used in a problem, not the underlying technique

DO NOT MERGE when items are genuinely different:
- Require different knowledge or techniques
- Would be separate topics in a course

Return JSON array of objects with:
- "canonical": A clean, concise English name for this concept (CREATE the best name, don't just pick from list)
- "members": Array of input names that belong to this group

Return [] if no groups found."""

        try:
            logger.info(f"Detecting synonyms among {len(unique_names)} {item_type} items")
            response = llm.generate(
                prompt=prompt,
                temperature=0.0,
                json_mode=True,
            )

            if response and response.text:
                logger.debug(f"Synonym detection raw response: {response.text[:500]}")
                groups = json.loads(response.text)
                # Validate structure - expect list of {"canonical": str, "members": [str]}
                if isinstance(groups, list):
                    for g in groups:
                        if isinstance(g, dict) and "canonical" in g and "members" in g:
                            if isinstance(g["members"], list) and len(g["members"]) >= 1:
                                all_groups.append((g["canonical"], item_type, g["members"]))
                    if all_groups:
                        logger.info(f"Detected {len(all_groups)} synonym groups for type {item_type}")

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse synonym detection response: {e}")
        except Exception as e:
            logger.warning(f"Synonym detection failed for type {item_type}: {e}")

    return all_groups


def filter_and_organize_knowledge(
    llm: LLMManager,
    items: list[dict],
    existing_parents: list[str],
    existing_topics: list[str] | None = None,  # Deprecated, ignored
) -> dict:
    """
    Filter extracted knowledge items using LLM.

    Uses coherence-based filtering:
    - Filter out outliers (context/scenario items, not academic concepts)
    - Normalize parent names to existing ones

    Args:
        llm: LLMManager instance
        items: List of extracted knowledge items with name, type, parent_name
        existing_parents: List of parent names already in the course
        existing_topics: DEPRECATED - ignored, kept for backward compatibility

    Returns:
        {
            "valid_items": [...],      # Items that passed filtering
            "filtered_items": [...],   # Items removed (with idx for debugging)
            "filtered_indices": [...], # Indices of filtered items
            "inferred_topics": [],     # DEPRECATED - always empty
        }
    """
    if not items:
        return {
            "valid_items": [],
            "filtered_items": [],
            "filtered_indices": [],
            "inferred_topics": [],
        }

    # Add index to each item for reliable matching (LLM may modify names)
    indexed_items = [{"idx": i, **item} for i, item in enumerate(items)]

    prompt = f"""Analyze these extracted knowledge items and filter out outliers.

ITEMS:
{json.dumps(indexed_items, indent=2, ensure_ascii=False)}

EXISTING PARENT CONCEPTS IN COURSE:
{json.dumps(existing_parents, ensure_ascii=False) if existing_parents else "[]"}

TASK:
1. AGGRESSIVELY Flag OUTLIERS using these tests:

   TEST A - Academic vs Context: "Is this item the SUBJECT of study, or just the SETTING/CONTEXT of a word problem?"
   TEST B - Textbook test: "Would this appear as a chapter heading or section title in this course's textbook?"
   TEST C - Lecture test: "Would a professor put this on a lecture slide as a concept to teach?"
   TEST D - Abstraction test: "Is this a general theoretical concept, or a specific real-world instance?"

   If ANY test fails → FILTER the item out

   Keep ONLY items where ALL tests pass

2. Normalize PARENTS - if an item suggests a parent similar to an existing one, use the existing name

CRITICAL: Each item has an "idx" field. You MUST return this idx unchanged for matching.

RETURN JSON:
{{
    "valid_indices": [0, 2, 4],
    "filtered_indices": [1, 3]
}}

NOTE: Just return the indices of valid vs filtered items.
"""

    try:
        response = llm.generate(
            prompt=prompt,
            temperature=0.3,
            json_mode=True,
        )

        if response and response.text:
            result = json.loads(response.text)

            # Get valid indices from result
            valid_indices = set(result.get("valid_indices", range(len(items))))
            filtered_indices = result.get("filtered_indices", [])

            # If LLM only returned filtered_indices, compute valid_indices
            if "valid_indices" not in result and filtered_indices:
                filtered_set = set(filtered_indices)
                valid_indices = {i for i in range(len(items)) if i not in filtered_set}

            # Build valid_items (original items that passed)
            valid_items = [items[i] for i in range(len(items)) if i in valid_indices]

            # Build filtered_items for logging
            filtered_items = [
                {"name": items[i].get("name", "unknown"), "idx": i}
                for i in filtered_indices
                if i < len(items)
            ]

            # Log filtered items for debugging
            if filtered_items:
                for item in filtered_items:
                    logger.info(f"Filtered: {item.get('name')} (idx={item.get('idx')})")

            return {
                "valid_items": valid_items,
                "filtered_items": filtered_items,
                "filtered_indices": list(filtered_indices),
                "inferred_topics": [],  # Deprecated
            }
        else:
            logger.warning("Post-processor got empty response, returning all items")
            return {
                "valid_items": items,
                "filtered_items": [],
                "filtered_indices": [],
                "inferred_topics": [],
            }

    except json.JSONDecodeError as e:
        logger.error(f"Post-processor JSON parse error: {e}")
        return {
            "valid_items": items,
            "filtered_items": [],
            "filtered_indices": [],
            "inferred_topics": [],
        }
    except Exception as e:
        logger.error(f"Post-processor error: {e}")
        return {
            "valid_items": items,
            "filtered_items": [],
            "filtered_indices": [],
            "inferred_topics": [],
        }
