import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.search.cost import CostCalculator


def test_cost_calculator():
    calculator = CostCalculator()

    html = {
        "id": 1,
        "name": "HTML",
        "difficulty": 1,
        "priority": 1.0,
        "canonical_position": 1,
    }

    css = {
        "id": 2,
        "name": "CSS",
        "difficulty": 2,
        "priority": 1.2,
        "canonical_position": 2,
    }

    javascript = {
        "id": 3,
        "name": "JavaScript",
        "difficulty": 3,
        "priority": 1.5,
        "canonical_position": 3,
    }

    html_cost = calculator.topic_cost(html, previous_topic=None, expected_position=1)
    assert html_cost == 1.0

    css_cost = calculator.topic_cost(css, previous_topic=html, expected_position=2)
    # priority 1.2 + difficulty jump (2-1)*2 = 2.0 + dev 0 = 3.2
    assert abs(css_cost - 3.2) < 1e-4

    js_cost = calculator.topic_cost(javascript, previous_topic=css, expected_position=3)
    # priority 1.5 + difficulty jump (3-2)*2 = 2.0 + dev 0 = 3.5
    assert abs(js_cost - 3.5) < 1e-4

    # Verify minimum_step_cost lower bound property
    assert calculator.minimum_step_cost(html) == 1.0
    assert calculator.minimum_step_cost(css) == 1.2
    assert calculator.minimum_step_cost(javascript) == 1.5
    assert calculator.minimum_step_cost() == 1.0
    assert calculator.minimum_step_cost(html) <= html_cost
    assert calculator.minimum_step_cost(css) <= css_cost
    assert calculator.minimum_step_cost(javascript) <= js_cost


if __name__ == "__main__":
    calculator = CostCalculator()
    html = {
        "id": 1,
        "name": "HTML",
        "difficulty": 1,
        "priority": 1.0,
        "canonical_position": 1,
    }
    css = {
        "id": 2,
        "name": "CSS",
        "difficulty": 2,
        "priority": 1.2,
        "canonical_position": 2,
    }
    javascript = {
        "id": 3,
        "name": "JavaScript",
        "difficulty": 3,
        "priority": 1.5,
        "canonical_position": 3,
    }
    print(
        "HTML cost:",
        calculator.topic_cost(html, previous_topic=None, expected_position=1),
    )
    print(
        "CSS cost:",
        calculator.topic_cost(css, previous_topic=html, expected_position=2),
    )
    print(
        "JavaScript cost:",
        calculator.topic_cost(
            javascript, previous_topic=css, expected_position=3
        ),
    )