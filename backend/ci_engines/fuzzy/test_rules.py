import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.fuzzy.rules import (
    get_rules,
    get_rule,
)


def test_fuzzy_rules():
    rules = get_rules()
    assert len(rules) == 9

    for rule in rules:
        assert "time" in rule
        assert "progress" in rule
        assert "output" in rule

    rule_sb = get_rule("Scarce", "Behind")
    assert rule_sb is not None
    assert rule_sb["output"] == "LargeIncrease"

    rule_so = get_rule("Scarce", "OnTrack")
    assert rule_so is not None
    assert rule_so["output"] == "SmallIncrease"

    rule_aa = get_rule("Adequate", "Ahead")
    assert rule_aa is not None
    assert rule_aa["output"] == "SmallDecrease"

    rule_am_ah = get_rule("Ample", "Ahead")
    assert rule_am_ah is not None
    assert rule_am_ah["output"] == "LargeDecrease"

    assert get_rule("NonExistent", "Behind") is None


if __name__ == "__main__":
    rules = get_rules()
    print("Total rules:", len(rules))
    print()
    print("Scarce + Behind:", get_rule("Scarce", "Behind"))
    print("Scarce + OnTrack:", get_rule("Scarce", "OnTrack"))
    print("Adequate + Ahead:", get_rule("Adequate", "Ahead"))
    print("Ample + Ahead:", get_rule("Ample", "Ahead"))
    print()
    print("All fuzzy rules:")
    for index, rule in enumerate(rules, start=1):
        print(
            f"Rule {index}: "
            f"IF Time is {rule['time']} "
            f"AND Progress is {rule['progress']} "
            f"THEN Adjustment is {rule['output']}"
        )