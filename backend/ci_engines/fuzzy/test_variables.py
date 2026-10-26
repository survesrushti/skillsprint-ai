import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.fuzzy.variables import FuzzyVariables


def test_fuzzy_variables():
    fuzzy = FuzzyVariables()

    # Time availability = 0.3 (Scarce)
    time_03 = fuzzy.time_availability(0.3)
    assert time_03["Scarce"] == (0.8 - 0.3) / 0.8
    assert time_03["Adequate"] == 0.0
    assert time_03["Ample"] == 0.0

    # Progress = 1.0 (OnTrack)
    prog_10 = fuzzy.progress(1.0)
    assert prog_10["Behind"] == 0.0
    assert prog_10["OnTrack"] == 1.0
    assert prog_10["Ahead"] == 0.0

    # Progress = 1.7 (Ahead)
    prog_17 = fuzzy.progress(1.7)
    assert prog_17["Behind"] == 0.0
    assert prog_17["OnTrack"] == 0.0
    assert abs(prog_17["Ahead"] - 0.625) < 1e-4

    # Workload adjustment = 0.15 (SmallIncrease peak)
    adj_15 = fuzzy.workload_adjustment(0.15)
    assert adj_15["SmallIncrease"] == 1.0
    assert adj_15["LargeIncrease"] == 0.0
    assert adj_15["NoChange"] == 0.0


if __name__ == "__main__":
    fuzzy = FuzzyVariables()
    print("Time Availability = 0.3")
    print(fuzzy.time_availability(0.3))
    print()
    print("Progress = 1.0")
    print(fuzzy.progress(1.0))
    print()
    print("Progress = 1.7")
    print(fuzzy.progress(1.7))
    print()
    print("Workload Adjustment = 0.15")
    print(fuzzy.workload_adjustment(0.15))