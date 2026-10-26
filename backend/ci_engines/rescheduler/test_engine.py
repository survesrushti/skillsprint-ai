import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.rescheduler.engine import Rescheduler


def test_rescheduler_evaluate():
    rescheduler = Rescheduler()

    result = rescheduler.evaluate(
        progress_ratio=0.6,
        available_minutes=120,
        required_minutes=180,
        missed_days=2,
        backlog_minutes=120,
        optional_topics_remaining=3,
        current_streak=2,
        recent_replans=1,
        days_remaining=5,
    )

    assert "fuzzy" in result
    assert "expert" in result
    assert "selected_strategy" in result
    assert result["selected_strategy"] == "COMPRESS"
    assert result["fuzzy"]["crisp_adjustment"] > 0
    assert len(result["expert"]["fired_rules"]) > 0


if __name__ == "__main__":
    rescheduler = Rescheduler()
    result = rescheduler.evaluate(
        progress_ratio=0.6,
        available_minutes=120,
        required_minutes=180,
        missed_days=2,
        backlog_minutes=120,
        optional_topics_remaining=3,
        current_streak=2,
        recent_replans=1,
        days_remaining=5,
    )
    print("=" * 60)
    print("RESCHEDULER TEST")
    print("=" * 60)
    print()
    print("Fuzzy workload adjustment:")
    print(result["fuzzy"]["crisp_adjustment"])
    print()
    print("Expert System strategy:")
    print(result["selected_strategy"])
    print()
    print("Fired Expert System rules:")
    for rule in result["expert"]["fired_rules"]:
        print(f"  {rule['rule_id']} -> {rule['strategy']}")
    print()
    print("Rescheduler test completed.")