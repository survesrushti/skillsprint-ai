import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.rescheduler.engine import Rescheduler


def test_rescheduler_full_with_search():
    rescheduler = Rescheduler()

    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60, "difficulty": 1},
        {"id": 2, "name": "CSS", "estimated_minutes": 90, "difficulty": 2},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120, "difficulty": 3},
        {"id": 4, "name": "React", "estimated_minutes": 150, "difficulty": 4},
    ]

    prerequisites = [
        (2, 1),
        (3, 1),
        (3, 2),
        (4, 3),
    ]

    selected_topics = {1, 2, 3, 4}
    completed_topics = set()

    result = rescheduler.evaluate(
        progress_ratio=0.6,
        available_minutes=120,
        required_minutes=420,
        missed_days=2,
        backlog_minutes=120,
        optional_topics_remaining=1,
        current_streak=2,
        recent_replans=1,
        days_remaining=5,
        topics=topics,
        prerequisites=prerequisites,
        selected_topics=selected_topics,
        completed_topics=completed_topics,
        study_hours_per_day=2,
    )

    # 1. Fuzzy Logic
    assert "fuzzy" in result
    assert result["fuzzy"]["crisp_adjustment"] > 0

    # 2. Expert System
    assert "expert" in result
    assert result["selected_strategy"] == "COMPRESS"

    # 3. A* Search
    search = result["search"]
    assert search is not None
    assert search["success"] is True
    assert search["sequence"] == [1, 2, 3, 4]
    assert search["total_minutes"] == 420
    assert search["total_days"] > 0
    assert len(search["daily_plan"]) > 0


if __name__ == "__main__":
    rescheduler = Rescheduler()
    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60, "difficulty": 1},
        {"id": 2, "name": "CSS", "estimated_minutes": 90, "difficulty": 2},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120, "difficulty": 3},
        {"id": 4, "name": "React", "estimated_minutes": 150, "difficulty": 4},
    ]
    prerequisites = [
        (2, 1),
        (3, 1),
        (3, 2),
        (4, 3),
    ]
    selected_topics = {1, 2, 3, 4}
    completed_topics = set()

    result = rescheduler.evaluate(
        progress_ratio=0.6,
        available_minutes=120,
        required_minutes=420,
        missed_days=2,
        backlog_minutes=120,
        optional_topics_remaining=1,
        current_streak=2,
        recent_replans=1,
        days_remaining=5,
        topics=topics,
        prerequisites=prerequisites,
        selected_topics=selected_topics,
        completed_topics=completed_topics,
        study_hours_per_day=2,
    )
    print("=" * 60)
    print("SKILLSPRINT FULL CI INTEGRATION")
    print("=" * 60)
    print()
    print("1. FUZZY LOGIC")
    print("-" * 30)
    print(
        "Time availability ratio:",
        round(result["fuzzy"]["time_availability_ratio"], 3),
    )
    print("Progress ratio:", result["fuzzy"]["progress_ratio"])
    print(
        "Workload adjustment:",
        round(result["fuzzy"]["crisp_adjustment"], 4),
    )
    print()
    print("2. EXPERT SYSTEM")
    print("-" * 30)
    print("Selected strategy:", result["selected_strategy"])
    for rule in result["expert"]["fired_rules"]:
        print(f"  {rule['rule_id']} -> {rule['strategy']}")
    print()
    print("3. A* SEARCH")
    print("-" * 30)
    search = result["search"]
    if search and search["success"]:
        print("Search successful:", search["success"])
        print("Sequence:", search["sequence"])
        print("Total minutes:", search["total_minutes"])
        print("Daily capacity:", search["daily_capacity"])
        print("Total days:", search["total_days"])
        print("Search cost:", search["search_cost"])
        print("Nodes expanded:", search["nodes_expanded"])
        print("\nDaily plan:")
        for day in search["daily_plan"]:
            print(day)
    else:
        print("Search failed.")
        if search:
            print("Message:", search["message"])
    print()
    print("=" * 60)
    print("FULL CI INTEGRATION TEST COMPLETED")
    print("=" * 60)