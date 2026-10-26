import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.search.capacity import CapacityCalculator


def test_capacity_calculator():
    calculator = CapacityCalculator(study_hours_per_day=2)

    assert calculator.daily_capacity() == 120
    assert calculator.total_capacity(10) == 1200
    assert calculator.can_complete(1000, 10) is True
    assert calculator.can_complete(1500, 10) is False
    assert calculator.remaining_capacity(1000, 10) == 200


if __name__ == "__main__":
    calculator = CapacityCalculator(study_hours_per_day=2)
    print("Daily capacity:", calculator.daily_capacity(), "minutes")
    print("10-day capacity:", calculator.total_capacity(10), "minutes")
    print("Can complete 1000 minutes:", calculator.can_complete(1000, 10))
    print("Can complete 1500 minutes:", calculator.can_complete(1500, 10))
    print(
        "Remaining capacity:",
        calculator.remaining_capacity(1000, 10),
        "minutes",
    )