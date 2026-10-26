import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.search.heuristic import HeuristicCalculator
from ci_engines.search.cost import CostCalculator


def test_heuristic_calculator():
    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60, "priority": 1.0},
        {"id": 2, "name": "CSS", "estimated_minutes": 90, "priority": 1.2},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120, "priority": 1.5},
    ]

    cost_calculator = CostCalculator()
    calculator = HeuristicCalculator(topics, cost_calculator=cost_calculator)
    remaining_topics = {2, 3}

    assert calculator.remaining_minutes(remaining_topics) == 210
    assert calculator.minimum_days_required(remaining_topics, daily_capacity=120) == 2
    # Admissible lower bound on cost: priority(2) + priority(3) = 1.2 + 1.5 = 2.7
    assert abs(calculator.estimate(remaining_topics, daily_capacity=120) - 2.7) < 1e-4

    # Test edge cases
    assert calculator.remaining_minutes(set()) == 0
    assert calculator.minimum_days_required(set(), daily_capacity=120) == 0
    assert calculator.estimate(set(), daily_capacity=120) == 0.0


def test_heuristic_admissibility_and_consistency():
    """
    Verify admissibility: h(n) <= h*(n).
    The heuristic estimate must never exceed the actual path cost to complete
    the remaining topics.
    """
    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60, "priority": 1.0, "difficulty": 1, "canonical_position": 1},
        {"id": 2, "name": "CSS", "estimated_minutes": 90, "priority": 1.2, "difficulty": 2, "canonical_position": 2},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120, "priority": 1.5, "difficulty": 3, "canonical_position": 3},
    ]

    cost_calc = CostCalculator()
    heuristic_calc = HeuristicCalculator(topics, cost_calculator=cost_calc)

    remaining = {2, 3}
    h_val = heuristic_calc.estimate(remaining)

    # Any sequence of completing topics 2 and 3:
    # Say sequence is 2 then 3, following topic 1
    topic1 = topics[0]
    topic2 = topics[1]
    topic3 = topics[2]

    cost_step2 = cost_calc.topic_cost(topic2, previous_topic=topic1, expected_position=2)
    cost_step3 = cost_calc.topic_cost(topic3, previous_topic=topic2, expected_position=3)
    actual_path_cost = cost_step2 + cost_step3

    assert h_val <= actual_path_cost, f"Heuristic {h_val} exceeds actual path cost {actual_path_cost}!"


if __name__ == "__main__":
    topics = [
        {"id": 1, "name": "HTML", "estimated_minutes": 60},
        {"id": 2, "name": "CSS", "estimated_minutes": 90},
        {"id": 3, "name": "JavaScript", "estimated_minutes": 120},
    ]
    calculator = HeuristicCalculator(topics)
    remaining_topics = {2, 3}
    print(
        "Remaining minutes:",
        calculator.remaining_minutes(remaining_topics),
    )
    print(
        "Minimum days required:",
        calculator.minimum_days_required(remaining_topics, daily_capacity=120),
    )
    print(
        "A* heuristic estimate:",
        calculator.estimate(remaining_topics, daily_capacity=120),
    )