"""
Post-processor for knowledge item validation.

Uses LLM to validate extracted items via coherence-based filtering.
Infers topics from validated knowledge items.
"""
import json
import logging
from typing import Any

from models.llm_manager import LLMManager

logger = logging.getLogger(__name__)


def filter_and_organize_knowledge(
    llm: LLMManager,
    items: list[dict],
    existing_parents: list[str],
    existing_topics: list[str],
) -> dict:
    """
    Filter extracted knowledge items and infer topics using LLM.

    Uses coherence-based filtering:
    - Identify the dominant concept cluster
    - Filter out outliers (context/scenario items)
    - Normalize parent names to existing ones
    - INFER appropriate topic from valid items (not from extraction)

    Args:
        llm: LLMManager instance
        items: List of extracted knowledge items with name, type, parent_name
        existing_parents: List of parent names already in the course
        existing_topics: List of topic names already in the course

    Returns:
        {
            "valid_items": [...],      # Items that passed filtering
            "filtered_items": [...],   # Items removed (with reasons)
            "inferred_topic": "...",   # Topic derived from valid items
        }
    """
    if not items:
        return {
            "valid_items": [],
            "filtered_items": [],
            "inferred_topic": None,
        }

    prompt = f"""Analyze these extracted knowledge items for coherence.

ITEMS:
{json.dumps(items, indent=2, ensure_ascii=False)}

EXISTING PARENT CONCEPTS IN COURSE:
{json.dumps(existing_parents, ensure_ascii=False) if existing_parents else "[]"}

EXISTING TOPICS IN COURSE:
{json.dumps(existing_topics, ensure_ascii=False) if existing_topics else "[]"}

TASK:
1. Identify the DOMINANT THEME - what field of study do most items belong to?
2. Flag OUTLIERS - items that don't fit the dominant theme
   - These are likely scenario/context from word problems, not course concepts
   - Test: "Is this something a student learns/studies, or just where the problem takes place?"
   - Test: "Would this appear in the course textbook as a topic to learn?"
3. Normalize PARENTS - if an item suggests a parent similar to an existing one, use the existing name
4. INFER TOPIC - based on valid items, what topic should they belong to?
   - Prefer existing topics if they fit
   - Topics should be chapter-level (not too broad, not too specific)

RETURN JSON:
{{
    "dominant_theme": "description of main concept area",
    "valid_items": [
        {{"name": "...", "knowledge_type": "...", "parent_name": "...", "reason": "fits theme"}}
    ],
    "filtered_items": [
        {{"name": "...", "reason": "why filtered"}}
    ],
    "inferred_topic": "topic name derived from valid items"
}}
"""

    try:
        response = llm.generate(
            prompt=prompt,
            temperature=0.3,
            json_mode=True,
        )

        if response and response.content:
            result = json.loads(response.content)

            # Log filtered items for debugging
            filtered = result.get("filtered_items", [])
            if filtered:
                for item in filtered:
                    logger.info(f"Filtered: {item.get('name')} - {item.get('reason')}")

            return result
        else:
            logger.warning("Post-processor got empty response, returning all items")
            return {
                "valid_items": items,
                "filtered_items": [],
                "inferred_topic": existing_topics[0] if existing_topics else None,
            }

    except json.JSONDecodeError as e:
        logger.error(f"Post-processor JSON parse error: {e}")
        return {
            "valid_items": items,
            "filtered_items": [],
            "inferred_topic": existing_topics[0] if existing_topics else None,
        }
    except Exception as e:
        logger.error(f"Post-processor error: {e}")
        return {
            "valid_items": items,
            "filtered_items": [],
            "inferred_topic": existing_topics[0] if existing_topics else None,
        }
