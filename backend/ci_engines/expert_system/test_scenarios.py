import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.expert_system.facts import LearningFacts
from ci_engines.expert_system.engine import ExpertSystem


def test_expert_system_scenarios():
    expert_system = ExpertSystem()

    scenarios = [
        {
            "name": "Behind + Missed Sessions",
            "facts": LearningFacts(
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
            ),
            "expected_strategy": "COMPRESS",
        },
        {
            "name": "Ahead Learner",
            "facts": LearningFacts(
                progress_ratio=1.4,
                available_minutes=300,
                required_minutes=180,
                missed_days=0,
                backlog_minutes=0,
                optional_topics_remaining=2,
                current_streak=8,
                recent_replans=0,
                fuzzy_adjustment=-0.20,
                days_remaining=7,
            ),
            "expected_strategy": "RELAX",
        },
        {
            "name": "On Track",
            "facts": LearningFacts(
                progress_ratio=1.0,
                available_minutes=180,
                required_minutes=180,
                missed_days=0,
                backlog_minutes=0,
                optional_topics_remaining=0,
                current_streak=5,
                recent_replans=0,
                fuzzy_adjustment=0.0,
                days_remaining=7,
            ),
            "expected_strategy": "NO_CHANGE",
        },
        {
            "name": "Critical Deadline",
            "facts": LearningFacts(
                progress_ratio=0.5,
                available_minutes=60,
                required_minutes=300,
                missed_days=4,
                backlog_minutes=240,
                optional_topics_remaining=2,
                current_streak=0,
                recent_replans=1,
                fuzzy_adjustment=0.30,
                days_remaining=1,
            ),
            "expected_strategy": "EXTEND_DEADLINE",
        },
    ]

    for scenario in scenarios:
        result = expert_system.evaluate(scenario["facts"])
        assert result["selected_strategy"] == scenario["expected_strategy"]
        assert len(result["fired_rules"]) > 0


if __name__ == "__main__":
    expert_system = ExpertSystem()
    scenarios = [
        {
            "name": "Behind + Missed Sessions",
            "facts": LearningFacts(
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
            ),
        },
        {
            "name": "Ahead Learner",
            "facts": LearningFacts(
                progress_ratio=1.4,
                available_minutes=300,
                required_minutes=180,
                missed_days=0,
                backlog_minutes=0,
                optional_topics_remaining=2,
                current_streak=8,
                recent_replans=0,
                fuzzy_adjustment=-0.20,
                days_remaining=7,
            ),
        },
        {
            "name": "On Track",
            "facts": LearningFacts(
                progress_ratio=1.0,
                available_minutes=180,
                required_minutes=180,
                missed_days=0,
                backlog_minutes=0,
                optional_topics_remaining=0,
                current_streak=5,
                recent_replans=0,
                fuzzy_adjustment=0.0,
                days_remaining=7,
            ),
        },
        {
            "name": "Critical Deadline",
            "facts": LearningFacts(
                progress_ratio=0.5,
                available_minutes=60,
                required_minutes=300,
                missed_days=4,
                backlog_minutes=240,
                optional_topics_remaining=2,
                current_streak=0,
                recent_replans=1,
                fuzzy_adjustment=0.30,
                days_remaining=1,
            ),
        },
    ]

    for scenario in scenarios:
        result = expert_system.evaluate(scenario["facts"])
        print("=" * 60)
        print("Scenario:", scenario["name"])
        print("Selected strategy:", result["selected_strategy"])
        print()
        print("Fired rules:")
        for rule in result["fired_rules"]:
            print(
                f"  {rule['rule_id']} -> "
                f"{rule['strategy']} "
                f"(Priority {rule['priority']})"
            )
        print()