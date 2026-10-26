import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.fuzzy.engine import FuzzyEngine


def test_fuzzy_engine():
    engine = FuzzyEngine()
    result = engine.calculate(
        time_availability_ratio=0.3,
        progress_ratio=0.6,
    )

    assert result["time_availability_ratio"] == 0.3
    assert result["progress_ratio"] == 0.6
    assert "time_memberships" in result
    assert "progress_memberships" in result
    assert "output_strengths" in result
    assert "crisp_adjustment" in result

    # When time is scarce and progress is behind, crisp adjustment should be positive (workload increase)
    assert 0.15 <= result["crisp_adjustment"] <= 0.35
    assert len(result["fired_rules"]) == 9


if __name__ == "__main__":
    engine = FuzzyEngine()
    result = engine.calculate(
        time_availability_ratio=0.3,
        progress_ratio=0.6,
    )
    print("Time availability ratio:")
    print(result["time_availability_ratio"])
    print()
    print("Progress ratio:")
    print(result["progress_ratio"])
    print()
    print("Time memberships:")
    print(result["time_memberships"])
    print()
    print("Progress memberships:")
    print(result["progress_memberships"])
    print()
    print("Output strengths:")
    for output, strength in result["output_strengths"].items():
        print(f"{output}: {strength:.3f}")
    print()
    print("Crisp workload adjustment:")
    print(f"{result['crisp_adjustment']:.4f}")
    print()
    print("Workload adjustment percentage:")
    print(f"{result['crisp_adjustment'] * 100:.2f}%")