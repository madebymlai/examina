#!/usr/bin/env python3
"""Quick script to inspect exercise data."""

import json
from storage.database import Database

def inspect_exercises(course_code, limit=10):
    """Inspect exercises for a course."""
    with Database() as db:
        exercises = db.get_exercises_by_course(course_code)

        print(f"\nCourse: {course_code}")
        print(f"Total exercises: {len(exercises)}\n")

        # Count topics and core loops
        topics = {}
        core_loops = {}

        for ex in exercises:
            topic = ex.get('topic') or 'None'
            core_loop = ex.get('core_loop_id') or 'None'

            topics[topic] = topics.get(topic, 0) + 1
            core_loops[core_loop] = core_loops.get(core_loop, 0) + 1

        print("Topic distribution:")
        for topic, count in sorted(topics.items(), key=lambda x: -x[1]):
            print(f"  {topic}: {count}")

        print("\nCore loop distribution:")
        for loop, count in sorted(core_loops.items(), key=lambda x: -x[1]):
            print(f"  {loop}: {count}")

        print(f"\n{'='*80}")
        print("Sample exercises:")
        print('='*80)

        for i, ex in enumerate(exercises[:limit]):
            print(f"\nExercise {i+1}: {ex['id']}")
            print(f"Topic: {ex.get('topic', 'None')}")
            print(f"Core loop: {ex.get('core_loop_id', 'None')}")
            print(f"Difficulty: {ex.get('difficulty', 'None')}")
            print(f"Text (first 300 chars):\n{ex['text'][:300]}...")
            print("-" * 80)

if __name__ == "__main__":
    import sys
    course = sys.argv[1] if len(sys.argv) > 1 else "B006802"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    inspect_exercises(course, limit)
