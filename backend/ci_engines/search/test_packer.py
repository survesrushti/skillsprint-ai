import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.search.packer import StudyPlanPacker


def test_study_plan_packer():
    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60},
        {"id": 2, "name": "CSS", "estimated_minutes": 90},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120},
        {"id": 4, "name": "React", "estimated_minutes": 150},
    ]

    packer = StudyPlanPacker(topics)
    topic_sequence = [1, 2, 3, 4]
    daily_capacity = 120

    days = packer.pack(
        topic_sequence=topic_sequence,
        daily_capacity=daily_capacity,
    )

    assert len(days) == 4
    assert packer.total_planned_minutes(days) == 420

    # Day 1: HTML (60) + CSS (60) = 120
    assert days[0]["day"] == 1
    assert sum(t["minutes"] for t in days[0]["tasks"]) == 120

    # Day 2: CSS (30) + JS (90) = 120
    assert days[1]["day"] == 2
    assert sum(t["minutes"] for t in days[1]["tasks"]) == 120

    # Day 3: JS (30) + React (90) = 120
    assert days[2]["day"] == 3
    assert sum(t["minutes"] for t in days[2]["tasks"]) == 120

    # Day 4: React (60) = 60
    assert days[3]["day"] == 4
    assert sum(t["minutes"] for t in days[3]["tasks"]) == 60


if __name__ == "__main__":
    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60},
        {"id": 2, "name": "CSS", "estimated_minutes": 90},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120},
        {"id": 4, "name": "React", "estimated_minutes": 150},
    ]
    packer = StudyPlanPacker(topics)
    topic_sequence = [1, 2, 3, 4]
    daily_capacity = 120
    days = packer.pack(
        topic_sequence=topic_sequence, daily_capacity=daily_capacity
    )
    print("Generated study plan:\n")
    for day in days:
        print(f"Day {day['day']}:")
        for task in day["tasks"]:
            print(f"  {task['topic_name']}: {task['minutes']} minutes")
        print()
    print("Total planned minutes:", packer.total_planned_minutes(days))