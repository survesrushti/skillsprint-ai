import os
import sys
from datetime import date, timedelta
from types import SimpleNamespace

# Ensure backend directory is in sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from routes.roadmap import _resolve_known_topics
from ci_engines.search.graph import TopicGraph
from ci_engines.search.cost import CostCalculator
from ci_engines.search.heuristic import HeuristicCalculator
from ci_engines.search.astar import AStarSearch
from ci_engines.search.engine import SearchEngine
from tests.jwt_test_helpers import get_auth_headers


MOCK_TOPICS = [
    {
        "id": 1,
        "name": "HTML Fundamentals",
        "slug": "html-fundamentals",
        "estimated_minutes": 180,
        "difficulty": 1,
        "priority": 1.0,
        "canonical_position": 1,
        "is_optional": False,
    },
    {
        "id": 2,
        "name": "CSS Fundamentals",
        "slug": "css-fundamentals",
        "estimated_minutes": 240,
        "difficulty": 1,
        "priority": 1.0,
        "canonical_position": 2,
        "is_optional": False,
    },
    {
        "id": 3,
        "name": "JavaScript Fundamentals",
        "slug": "javascript-fundamentals",
        "estimated_minutes": 360,
        "difficulty": 2,
        "priority": 1.2,
        "canonical_position": 3,
        "is_optional": False,
    },
    {
        "id": 4,
        "name": "Git and GitHub",
        "slug": "git-and-github",
        "estimated_minutes": 180,
        "difficulty": 1,
        "priority": 0.9,
        "canonical_position": 4,
        "is_optional": True,
    },
    {
        "id": 5,
        "name": "React Fundamentals",
        "slug": "react-fundamentals",
        "estimated_minutes": 360,
        "difficulty": 3,
        "priority": 1.3,
        "canonical_position": 5,
        "is_optional": False,
    },
]

MOCK_PREREQUISITES = [
    (2, 1),       # CSS requires HTML
    (3, 1),       # JavaScript requires HTML
    (3, 2),       # JavaScript requires CSS
    (4, 1),       # Git requires HTML
    (5, 3),       # React requires JavaScript
]


# ============================================================================
# UNIT TESTS: _resolve_known_topics
# ============================================================================

def test_resolve_known_topics_empty_or_none():
    assert _resolve_known_topics(None, MOCK_TOPICS) == set()
    assert _resolve_known_topics("", MOCK_TOPICS) == set()
    assert _resolve_known_topics([], MOCK_TOPICS) == set()
    assert _resolve_known_topics("   ", MOCK_TOPICS) == set()


def test_resolve_known_topics_exact_name():
    result = _resolve_known_topics("HTML Fundamentals", MOCK_TOPICS)
    assert result == {1}


def test_resolve_known_topics_exact_slug():
    result = _resolve_known_topics("html-fundamentals", MOCK_TOPICS)
    assert result == {1}


def test_resolve_known_topics_case_insensitive_and_normalized():
    assert _resolve_known_topics("html fundamentals", MOCK_TOPICS) == {1}
    assert _resolve_known_topics("HTML FUNDAMENTALS", MOCK_TOPICS) == {1}
    assert _resolve_known_topics("  css-fundamentals  ", MOCK_TOPICS) == {2}
    assert _resolve_known_topics("css fundamentals", MOCK_TOPICS) == {2}


def test_resolve_known_topics_keyword_matching():
    # Distinctive keyword matches unique topic name in track
    assert _resolve_known_topics("HTML", MOCK_TOPICS) == {1}
    assert _resolve_known_topics("CSS", MOCK_TOPICS) == {2}
    assert _resolve_known_topics("React", MOCK_TOPICS) == {5}


def test_resolve_known_topics_comma_separated_and_lists():
    csv_input = "HTML Fundamentals, CSS Fundamentals"
    assert _resolve_known_topics(csv_input, MOCK_TOPICS) == {1, 2}

    list_input = ["html-fundamentals", "react-fundamentals"]
    assert _resolve_known_topics(list_input, MOCK_TOPICS) == {1, 5}


def test_resolve_known_topics_with_unmatched_and_objects():
    # Ignore unknown topics gracefully without errors
    mixed_input = "HTML Fundamentals, Quantum Computing, CSS Fundamentals"
    assert _resolve_known_topics(mixed_input, MOCK_TOPICS) == {1, 2}

    # Verify compatibility with SimpleNamespace or model-like objects
    objects = [
        SimpleNamespace(id=1, name="HTML Fundamentals", slug="html-fundamentals"),
        SimpleNamespace(id=2, name="CSS Fundamentals", slug="css-fundamentals"),
    ]
    assert _resolve_known_topics("HTML Fundamentals", objects) == {1}


# ============================================================================
# INTEGRATION TESTS: A* Search with Known Topics and Prerequisites
# ============================================================================

def test_search_baseline_without_known_topics():
    engine = SearchEngine()
    result = engine.generate_roadmap(
        topics=MOCK_TOPICS,
        prerequisites=MOCK_PREREQUISITES,
        selected_topics={1, 2, 3, 5},
        completed_topics=set(),
        study_hours_per_day=2,
    )

    assert result["success"] is True
    # In canonical topological order
    assert result["sequence"] == [1, 2, 3, 5]
    # Starts on Day 1 with HTML Fundamentals
    first_task = result["daily_plan"][0]["tasks"][0]
    assert first_task["topic_id"] == 1
    assert first_task["topic_name"] == "HTML Fundamentals"


def test_search_skips_known_topic_and_starts_on_prerequisite_dependent():
    """
    Core SRS requirement: When user knows HTML Fundamentals,
    HTML is excluded from the roadmap and the plan starts directly on CSS Fundamentals.
    """
    known_topics = {1}  # HTML Fundamentals is already completed
    engine = SearchEngine()

    result = engine.generate_roadmap(
        topics=MOCK_TOPICS,
        prerequisites=MOCK_PREREQUISITES,
        selected_topics={1, 2, 3, 5},
        completed_topics=known_topics,
        study_hours_per_day=2,
    )

    assert result["success"] is True
    assert 1 not in result["sequence"]
    assert result["sequence"] == [2, 3, 5]

    # Verify Day 1 schedule starts directly on CSS Fundamentals
    first_day_tasks = result["daily_plan"][0]["tasks"]
    assert len(first_day_tasks) > 0
    assert first_day_tasks[0]["topic_id"] == 2
    assert first_day_tasks[0]["topic_name"] == "CSS Fundamentals"
    # Ensure HTML is nowhere in any day of the roadmap
    all_scheduled_ids = {
        task["topic_id"]
        for day in result["daily_plan"]
        for task in day["tasks"]
    }
    assert 1 not in all_scheduled_ids


def test_prerequisite_dependency_enforced_when_only_partial_prerequisites_known():
    """
    JavaScript requires both HTML (1) and CSS (2).
    If only HTML is known, CSS must still precede JavaScript.
    """
    known_topics = {1}
    engine = SearchEngine()

    result = engine.generate_roadmap(
        topics=MOCK_TOPICS,
        prerequisites=MOCK_PREREQUISITES,
        selected_topics={1, 2, 3, 5},
        completed_topics=known_topics,
        study_hours_per_day=2,
    )

    sequence = result["sequence"]
    assert sequence.index(2) < sequence.index(3)
    assert sequence.index(3) < sequence.index(5)


def test_chain_of_prerequisites_unlocked_when_multiple_prerequisites_known():
    """
    When both HTML (1) and CSS (2) are known, JavaScript (3) is immediately
    available and starts on Day 1.
    """
    known_topics = {1, 2}
    engine = SearchEngine()

    result = engine.generate_roadmap(
        topics=MOCK_TOPICS,
        prerequisites=MOCK_PREREQUISITES,
        selected_topics={1, 2, 3, 5},
        completed_topics=known_topics,
        study_hours_per_day=2,
    )

    assert result["success"] is True
    assert 1 not in result["sequence"]
    assert 2 not in result["sequence"]
    assert result["sequence"] == [3, 5]

    first_task = result["daily_plan"][0]["tasks"][0]
    assert first_task["topic_id"] == 3
    assert first_task["topic_name"] == "JavaScript Fundamentals"


# ============================================================================
# END-TO-END FLASK TEST CLIENT INTEGRATION
# ============================================================================

def test_flask_generate_roadmap_with_known_topics():
    """
    Full end-to-end test using Flask test client with database persistence.
    """
    from app import create_app
    from extensions import db
    from models import Goal, Track, Topic, TopicPrerequisite

    app = create_app()

    with app.app_context():
        # Find or use the full-stack track (seeded in database)
        track = Track.query.filter_by(slug="full-stack-development").first()
        if not track:
            # If database not seeded, skip database integration
            return

        # Create a test goal with "HTML Fundamentals" as known topic
        target = date.today() + timedelta(days=60)
        formatted_target = target.strftime("%d/%m/%Y")

        headers = get_auth_headers("known_topics_user_1")
        with app.test_client() as client:
            goal_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": formatted_target,
                    "known_topics": ["HTML Fundamentals"],
                    "commitment": True,
                },
            )

            assert goal_res.status_code == 201
            goal_data = goal_res.get_json()
            goal_id = goal_data["goal"]["id"]

            # Generate roadmap
            gen_res = client.post(
                "/api/v1/roadmap/generate",
                headers=headers,
                json={"goal_id": goal_id},
            )

            assert gen_res.status_code == 200
            gen_data = gen_res.get_json()
            assert gen_data["status"] == "success"

            daily_plan = gen_data["roadmap"]
            assert len(daily_plan) > 0

            # Day 1 and all subsequent days must NOT include HTML Fundamentals
            all_scheduled_topic_names = [
                task["name"]
                for day in daily_plan
                for task in day["tasks"]
            ]
            assert "HTML Fundamentals" not in all_scheduled_topic_names

            # CSS Fundamentals must be scheduled in the roadmap
            assert any("CSS Fundamentals" in name for name in all_scheduled_topic_names)

            # Verify known_topics is returned in goal metadata
            assert "HTML Fundamentals" in gen_data["goal"]["known_topics"]


def test_flask_generate_roadmap_data_analytics_known_topic():
    """
    Test with Data Analytics track where all topics depend on Python Fundamentals.
    When Python Fundamentals is known, it is excluded and dependent topics are unlocked.
    """
    from app import create_app
    from extensions import db
    from models import Track

    app = create_app()

    with app.app_context():
        track = Track.query.filter_by(slug="data-analytics").first()
        if not track:
            return

        target = date.today() + timedelta(days=60)
        formatted_target = target.strftime("%d/%m/%Y")

        headers = get_auth_headers("known_topics_user_data_analytics")
        with app.test_client() as client:
            goal_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": formatted_target,
                    "known_topics": ["Python Fundamentals"],
                    "commitment": True,
                },
            )

            assert goal_res.status_code == 201
            goal_id = goal_res.get_json()["goal"]["id"]

            gen_res = client.post(
                "/api/v1/roadmap/generate",
                headers=headers,
                json={"goal_id": goal_id},
            )

            assert gen_res.status_code == 200
            gen_data = gen_res.get_json()
            daily_plan = gen_data["roadmap"]
            assert len(daily_plan) > 0

            all_scheduled = [
                task["name"]
                for day in daily_plan
                for task in day["tasks"]
            ]

            # Python Fundamentals must be completely excluded
            assert "Python Fundamentals" not in all_scheduled

            # Day 1 must start on an unlocked dependent topic (e.g. Statistics, NumPy, or Pandas)
            day_1_tasks = daily_plan[0]["tasks"]
            assert len(day_1_tasks) > 0
            assert day_1_tasks[0]["name"] != "Python Fundamentals"
