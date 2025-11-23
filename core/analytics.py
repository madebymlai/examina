"""
Progress analytics for Examina.
Tracks student progress, mastery levels, and spaced repetition.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from storage.database import Database
from config import Config


class ProgressAnalytics:
    """Analytics engine for student progress and mastery tracking."""

    def __init__(self):
        """Initialize analytics engine."""
        pass

    def get_course_summary(self, course_code: str) -> Dict[str, Any]:
        """Get overall course progress statistics.

        Args:
            course_code: Course code

        Returns:
            Dictionary with:
            - total_exercises: Total unique exercises
            - exercises_attempted: Number of exercises attempted
            - exercises_mastered: Number of exercises mastered
            - overall_mastery: Average mastery score (0-1)
            - quiz_sessions_completed: Number of completed quiz sessions
            - avg_score: Average quiz score
            - total_time_spent: Total time spent in minutes
            - core_loops_discovered: Number of core loops found
            - topics_discovered: Number of topics found
        """
        with Database() as db:
            # Total exercises (excluding low confidence skipped)
            total_exercises = db.conn.execute("""
                SELECT COUNT(DISTINCT id)
                FROM exercises
                WHERE course_code = ? AND analyzed = 1 AND low_confidence_skipped = 0
            """, (course_code,)).fetchone()[0]

            # Core loops and topics discovered
            core_loops_count = db.conn.execute("""
                SELECT COUNT(DISTINCT cl.id)
                FROM core_loops cl
                JOIN topics t ON cl.topic_id = t.id
                WHERE t.course_code = ?
            """, (course_code,)).fetchone()[0]

            topics_count = db.conn.execute("""
                SELECT COUNT(*)
                FROM topics
                WHERE course_code = ?
            """, (course_code,)).fetchone()[0]

            # Student progress stats
            progress_stats = db.conn.execute("""
                SELECT
                    COUNT(DISTINCT core_loop_id) as loops_attempted,
                    AVG(mastery_score) as avg_mastery
                FROM student_progress
                WHERE course_code = ? AND total_attempts > 0
            """, (course_code,)).fetchone()

            loops_attempted = progress_stats[0] or 0
            avg_mastery = progress_stats[1] or 0.0

            # Quiz session stats
            quiz_stats = db.conn.execute("""
                SELECT
                    COUNT(*) as completed_sessions,
                    AVG(score) as avg_score,
                    SUM(time_spent) as total_time
                FROM quiz_sessions
                WHERE course_code = ? AND completed_at IS NOT NULL
            """, (course_code,)).fetchone()

            completed_sessions = quiz_stats[0] or 0
            avg_score = quiz_stats[1] or 0.0
            total_time = quiz_stats[2] or 0

            # Calculate exercises attempted and mastered
            # An exercise is "attempted" if it appears in quiz_answers
            exercises_attempted = db.conn.execute("""
                SELECT COUNT(DISTINCT qa.exercise_id)
                FROM quiz_answers qa
                JOIN quiz_sessions qs ON qa.session_id = qs.id
                WHERE qs.course_code = ?
            """, (course_code,)).fetchone()[0]

            # An exercise is "mastered" if the core loop it belongs to has mastery >= threshold
            exercises_mastered = db.conn.execute("""
                SELECT COUNT(DISTINCT e.id)
                FROM exercises e
                JOIN student_progress sp ON e.core_loop_id = sp.core_loop_id
                WHERE e.course_code = ? AND sp.mastery_score >= ?
            """, (course_code, Config.MASTERY_THRESHOLD)).fetchone()[0]

            return {
                'total_exercises': total_exercises,
                'exercises_attempted': exercises_attempted,
                'exercises_mastered': exercises_mastered,
                'overall_mastery': avg_mastery,
                'quiz_sessions_completed': completed_sessions,
                'avg_score': avg_score,
                'total_time_spent': total_time // 60 if total_time else 0,  # Convert to minutes
                'core_loops_discovered': core_loops_count,
                'core_loops_attempted': loops_attempted,
                'topics_discovered': topics_count
            }

    def get_topic_breakdown(self, course_code: str) -> List[Dict[str, Any]]:
        """Get mastery breakdown per topic.

        Args:
            course_code: Course code

        Returns:
            List of dictionaries with:
            - topic_id: Topic ID
            - topic_name: Topic name
            - core_loops_count: Number of core loops
            - exercises_count: Number of exercises
            - mastery_score: Average mastery (0-1)
            - exercises_attempted: Number attempted
            - exercises_mastered: Number mastered
            - status: 'mastered', 'in_progress', 'weak', or 'not_started'
        """
        with Database() as db:
            topics = db.get_topics_by_course(course_code)
            breakdown = []

            for topic in topics:
                topic_id = topic['id']

                # Core loops in this topic
                core_loops = db.get_core_loops_by_topic(topic_id)
                core_loops_count = len(core_loops)

                # Exercises in this topic
                exercises_count = db.conn.execute("""
                    SELECT COUNT(*)
                    FROM exercises
                    WHERE topic_id = ? AND analyzed = 1 AND low_confidence_skipped = 0
                """, (topic_id,)).fetchone()[0]

                # Average mastery for this topic
                mastery_data = db.conn.execute("""
                    SELECT
                        AVG(sp.mastery_score) as avg_mastery,
                        COUNT(DISTINCT sp.core_loop_id) as loops_attempted
                    FROM student_progress sp
                    JOIN core_loops cl ON sp.core_loop_id = cl.id
                    WHERE cl.topic_id = ? AND sp.total_attempts > 0
                """, (topic_id,)).fetchone()

                avg_mastery = mastery_data[0] or 0.0
                loops_attempted = mastery_data[1] or 0

                # Exercises attempted and mastered
                exercises_attempted = db.conn.execute("""
                    SELECT COUNT(DISTINCT qa.exercise_id)
                    FROM quiz_answers qa
                    JOIN quiz_sessions qs ON qa.session_id = qs.id
                    JOIN exercises e ON qa.exercise_id = e.id
                    WHERE qs.course_code = ? AND e.topic_id = ?
                """, (course_code, topic_id)).fetchone()[0]

                exercises_mastered = db.conn.execute("""
                    SELECT COUNT(DISTINCT e.id)
                    FROM exercises e
                    JOIN student_progress sp ON e.core_loop_id = sp.core_loop_id
                    WHERE e.topic_id = ? AND sp.mastery_score >= ?
                """, (topic_id, Config.MASTERY_THRESHOLD)).fetchone()[0]

                # Determine status
                if loops_attempted == 0:
                    status = 'not_started'
                elif avg_mastery >= Config.MASTERY_THRESHOLD:
                    status = 'mastered'
                elif avg_mastery >= 0.5:
                    status = 'in_progress'
                else:
                    status = 'weak'

                breakdown.append({
                    'topic_id': topic_id,
                    'topic_name': topic['name'],
                    'core_loops_count': core_loops_count,
                    'exercises_count': exercises_count,
                    'mastery_score': avg_mastery,
                    'exercises_attempted': exercises_attempted,
                    'exercises_mastered': exercises_mastered,
                    'loops_attempted': loops_attempted,
                    'status': status
                })

            # Sort by mastery score ascending (weak areas first)
            breakdown.sort(key=lambda x: (x['status'] != 'weak', x['mastery_score']))

            return breakdown

    def get_weak_areas(self, course_code: str, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Identify topics and core loops below mastery threshold.

        Args:
            course_code: Course code
            threshold: Mastery threshold (default: 0.5)

        Returns:
            List of dictionaries with:
            - type: 'topic' or 'core_loop'
            - name: Topic or core loop name
            - mastery_score: Current mastery (0-1)
            - attempts: Number of attempts
            - last_practiced: Last practice timestamp
        """
        with Database() as db:
            weak_areas = []

            # Find weak core loops
            weak_loops = db.conn.execute("""
                SELECT
                    cl.id,
                    cl.name,
                    t.name as topic_name,
                    sp.mastery_score,
                    sp.total_attempts,
                    sp.last_practiced
                FROM student_progress sp
                JOIN core_loops cl ON sp.core_loop_id = cl.id
                JOIN topics t ON cl.topic_id = t.id
                WHERE t.course_code = ?
                    AND sp.mastery_score < ?
                    AND sp.total_attempts > 0
                ORDER BY sp.mastery_score ASC
            """, (course_code, threshold)).fetchall()

            for loop in weak_loops:
                weak_areas.append({
                    'type': 'core_loop',
                    'id': loop[0],
                    'name': loop[1],
                    'topic_name': loop[2],
                    'mastery_score': loop[3],
                    'attempts': loop[4],
                    'last_practiced': loop[5]
                })

            return weak_areas

    def get_due_reviews(self, course_code: str) -> List[Dict[str, Any]]:
        """Get exercises/core loops due for review today using SM-2 algorithm.

        Args:
            course_code: Course code

        Returns:
            List of dictionaries with:
            - core_loop_id: Core loop ID
            - core_loop_name: Core loop name
            - topic_name: Topic name
            - mastery_score: Current mastery
            - next_review: Scheduled review date
            - days_overdue: Days overdue (0 if due today)
            - priority: 'overdue' or 'due_today'
        """
        with Database() as db:
            today = datetime.now().date()

            # Get core loops due for review
            due_reviews = db.conn.execute("""
                SELECT
                    sp.core_loop_id,
                    cl.name as core_loop_name,
                    t.name as topic_name,
                    sp.mastery_score,
                    sp.next_review,
                    sp.last_practiced
                FROM student_progress sp
                JOIN core_loops cl ON sp.core_loop_id = cl.id
                JOIN topics t ON cl.topic_id = t.id
                WHERE t.course_code = ?
                    AND sp.next_review IS NOT NULL
                    AND DATE(sp.next_review) <= DATE('now')
                ORDER BY sp.next_review ASC
            """, (course_code,)).fetchall()

            reviews = []
            for review in due_reviews:
                next_review_date = datetime.fromisoformat(review[4]).date()
                days_overdue = (today - next_review_date).days

                reviews.append({
                    'core_loop_id': review[0],
                    'core_loop_name': review[1],
                    'topic_name': review[2],
                    'mastery_score': review[3],
                    'next_review': review[4],
                    'last_practiced': review[5],
                    'days_overdue': days_overdue,
                    'priority': 'overdue' if days_overdue > 0 else 'due_today'
                })

            return reviews

    def get_study_suggestions(self, course_code: Optional[str] = None) -> List[str]:
        """Generate personalized study suggestions.

        Priority:
        1. Overdue reviews (spaced repetition)
        2. Due reviews
        3. Weak areas (mastery < 0.5)
        4. New content (not yet attempted)

        Args:
            course_code: Optional course code to filter by

        Returns:
            List of suggestion strings
        """
        suggestions = []

        if not course_code:
            # Get all courses with progress
            with Database() as db:
                courses = db.conn.execute("""
                    SELECT DISTINCT course_code
                    FROM student_progress
                    WHERE total_attempts > 0
                """).fetchall()

                if not courses:
                    return ["No progress yet. Start by taking a quiz!"]

                course_code = courses[0][0]  # Default to first course with progress

        # 1. Check for overdue reviews
        due_reviews = self.get_due_reviews(course_code)
        overdue = [r for r in due_reviews if r['priority'] == 'overdue']
        due_today = [r for r in due_reviews if r['priority'] == 'due_today']

        if overdue:
            count = len(overdue)
            suggestions.append(f"🔴 {count} overdue review{'s' if count > 1 else ''}: {', '.join([r['core_loop_name'] for r in overdue[:3]])}")

        if due_today:
            count = len(due_today)
            suggestions.append(f"🟡 {count} review{'s' if count > 1 else ''} due today: {', '.join([r['core_loop_name'] for r in due_today[:3]])}")

        # 2. Check for weak areas
        weak_areas = self.get_weak_areas(course_code, threshold=0.5)
        if weak_areas:
            count = len(weak_areas)
            suggestions.append(f"⚠️  {count} weak area{'s' if count > 1 else ''}: {', '.join([w['name'] for w in weak_areas[:3]])}")

        # 3. Check for new content
        with Database() as db:
            # Core loops not yet attempted
            new_loops = db.conn.execute("""
                SELECT cl.id, cl.name, t.name as topic_name
                FROM core_loops cl
                JOIN topics t ON cl.topic_id = t.id
                LEFT JOIN student_progress sp ON cl.id = sp.core_loop_id AND sp.course_code = ?
                WHERE t.course_code = ? AND (sp.total_attempts IS NULL OR sp.total_attempts = 0)
                LIMIT 5
            """, (course_code, course_code)).fetchall()

            if new_loops:
                count = len(new_loops)
                suggestions.append(f"✨ {count} new topic{'s' if count > 1 else ''} to explore: {', '.join([loop[1] for loop in new_loops[:3]])}")

        # 4. Encouragement if doing well
        summary = self.get_course_summary(course_code)
        if summary['overall_mastery'] >= Config.MASTERY_THRESHOLD:
            suggestions.append(f"🎯 Great progress! Overall mastery: {summary['overall_mastery']:.1%}")

        if not suggestions:
            suggestions.append("🚀 Start a quiz to begin building your mastery!")

        return suggestions

    def get_core_loop_progress(self, course_code: str, core_loop_id: str) -> Dict[str, Any]:
        """Get detailed progress for a specific core loop.

        Args:
            course_code: Course code
            core_loop_id: Core loop ID

        Returns:
            Dictionary with progress details
        """
        with Database() as db:
            progress = db.conn.execute("""
                SELECT *
                FROM student_progress
                WHERE course_code = ? AND core_loop_id = ?
            """, (course_code, core_loop_id)).fetchone()

            if not progress:
                return {
                    'mastery_score': 0.0,
                    'total_attempts': 0,
                    'correct_attempts': 0,
                    'accuracy': 0.0,
                    'last_practiced': None,
                    'next_review': None,
                    'review_interval': 1
                }

            return {
                'mastery_score': progress['mastery_score'],
                'total_attempts': progress['total_attempts'],
                'correct_attempts': progress['correct_attempts'],
                'accuracy': progress['correct_attempts'] / progress['total_attempts'] if progress['total_attempts'] > 0 else 0.0,
                'last_practiced': progress['last_practiced'],
                'next_review': progress['next_review'],
                'review_interval': progress['review_interval']
            }
