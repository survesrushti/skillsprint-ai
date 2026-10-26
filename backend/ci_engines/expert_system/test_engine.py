import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.expert_system.facts import LearningFacts
from ci_engines.expert_system.engine import ExpertSystem


def test_expert_system_evaluate():
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

    expert_system = ExpertSystem()
    result = expert_system.evaluate(facts)

    assert result["selected_strategy"] == "COMPRESS"
    assert result["strategy"]["name"] == "Compress"
    assert "description" in result["strategy"]
    assert len(result["trace"]) > 0
    assert len(result["fired_rules"]) > 0


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
    expert_system = ExpertSystem()
    result = expert_system.evaluate(facts)

    print("Selected strategy:")
    print("==================")
    print(result["selected_strategy"])
    print()
    print("Explanation Trace:")
    print("==================")
    for step in result["trace"]:
        print(f"Step {step['step']}: {step['message']}")
        if step["type"] == "rule":
            print(f"  Rule: {step['rule_id']}")
            print(f"  Strategy: {step['strategy']}")
            print(f"  Priority: {step['priority']}")
    print()
    print("Final explanation:")
    print("==================")
    for step in result["trace"]:
        if step["type"] == "rule":
            print(f"- {step['rule_id']}: {step['message']}")
    print()
    print("Decision:", result["selected_strategy"])
    print("Description:", result["strategy"]["description"])