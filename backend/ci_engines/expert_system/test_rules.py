import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.expert_system.rules import (
    get_rules,
    get_rules_by_priority,
)


def test_expert_rules():
    rules = get_rules()
    assert len(rules) == 14

    # Ensure all rules have required fields
    for rule in rules:
        assert "id" in rule
        assert "condition" in rule
        assert "strategy" in rule
        assert "priority" in rule
        assert "reason" in rule


def test_expert_rules_priority_order():
    prioritized = get_rules_by_priority()
    assert len(prioritized) == 14

    # Ensure strictly descending priority
    priorities = [r["priority"] for r in prioritized]
    assert priorities == sorted(priorities, reverse=True)

    highest = prioritized[0]
    assert highest["id"] == "R1"
    assert highest["priority"] == 100
    assert highest["strategy"] == "EXTEND_DEADLINE"

    lowest = prioritized[-1]
    assert lowest["id"] == "R14"
    assert lowest["priority"] == 0
    assert lowest["strategy"] == "NO_CHANGE"


if __name__ == "__main__":
    rules = get_rules()
    print("Total expert rules:", len(rules))
    print()
    print("Rules by priority:")
    print("===================")
    for rule in get_rules_by_priority():
        print(
            f"{rule['id']} | "
            f"Priority: {rule['priority']} | "
            f"{rule['condition']} -> "
            f"{rule['strategy']}"
        )
    print()
    print("Highest priority rule:")
    highest = get_rules_by_priority()[0]
    print(
        f"{highest['id']}: "
        f"{highest['condition']} -> "
        f"{highest['strategy']}"
    )
    print(f"Reason: {highest['reason']}")