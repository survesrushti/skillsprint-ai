import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.fuzzy.variables import FuzzyVariables
from ci_engines.fuzzy.rules import get_rules
from ci_engines.fuzzy.inference import MamdaniInference


def test_mamdani_inference():
    fuzzy = FuzzyVariables()
    time_memberships = fuzzy.time_availability(0.3)
    progress_memberships = fuzzy.progress(0.6)

    inference = MamdaniInference(rules=get_rules())
    result = inference.evaluate(
        time_memberships=time_memberships,
        progress_memberships=progress_memberships,
    )

    assert "fired_rules" in result
    assert "output_strengths" in result
    assert len(result["fired_rules"]) == 9

    # Check firing strengths bounds
    for rule in result["fired_rules"]:
        assert 0.0 <= rule["firing_strength"] <= 1.0

    # For time=0.3 and progress=0.6:
    # time Scarce = 0.625, progress Behind = 0.25
    # Rule 1 (Scarce + Behind -> LargeIncrease): min(0.625, 0.25) = 0.25
    assert result["output_strengths"]["LargeIncrease"] > 0
    assert abs(result["output_strengths"]["LargeIncrease"] - 0.25) < 1e-4


if __name__ == "__main__":
    fuzzy = FuzzyVariables()
    time_memberships = fuzzy.time_availability(0.3)
    progress_memberships = fuzzy.progress(0.6)
    inference = MamdaniInference(rules=get_rules())
    result = inference.evaluate(
        time_memberships=time_memberships,
        progress_memberships=progress_memberships,
    )
    print("Time memberships:")
    print(time_memberships)
    print()
    print("Progress memberships:")
    print(progress_memberships)
    print()
    print("Rule firing strengths:")
    for rule in result["fired_rules"]:
        print(
            f"Rule {rule['rule_number']}: "
            f"{rule['time']} + {rule['progress']} "
            f"-> {rule['output']} "
            f"= {rule['firing_strength']:.3f}"
        )
    print()
    print("Final output strengths:")
    for output, strength in result["output_strengths"].items():
        print(f"{output}: {strength:.3f}")