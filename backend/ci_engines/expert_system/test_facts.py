import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.expert_system.facts import LearningFacts


def test_learning_facts():
    facts = LearningFacts(
        progress_ratio=0.6,
        available_minutes=120,
        required_minutes=180,
        missed_days=2,
        backlog_minutes=120,
        optional_topics_remaining=3,
        current_streak=2,
        recent_replans=1,
        fuzzy_adjustment=0.2152,
        days_remaining=5,
    )

    data = facts.to_dict()
    assert data["progress_ratio"] == 0.6
    assert data["available_minutes"] == 120
    assert data["required_minutes"] == 180
    assert data["missed_days"] == 2
    assert data["backlog_minutes"] == 120
    assert data["optional_topics_remaining"] == 3
    assert data["current_streak"] == 2
    assert data["recent_replans"] == 1
    assert data["fuzzy_adjustment"] == 0.2152
    assert data["days_remaining"] == 5


if __name__ == "__main__":
    facts = LearningFacts(
        progress_ratio=0.6,
        available_minutes=120,
        required_minutes=180,
        missed_days=2,
        backlog_minutes=120,
        optional_topics_remaining=3,
        current_streak=2,
        recent_replans=1,
        fuzzy_adjustment=0.2152,
        days_remaining=5,
    )
    print("Learning Facts")
    print("================")
    for name, value in facts.to_dict().items():
        print(f"{name}: {value}")