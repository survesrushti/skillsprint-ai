import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.rescheduler.engine import Rescheduler


def test_rescheduler_ci_pipeline():
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

    # Step 1: Fuzzy Logic
    assert "fuzzy" in result
    fuzzy = result["fuzzy"]
    assert round(fuzzy["time_availability_ratio"], 3) == round(120 / 180, 3)
    assert fuzzy["progress_ratio"] == 0.6
    assert fuzzy["crisp_adjustment"] > 0

    # Step 2: Expert System
    assert "expert" in result
    expert = result["expert"]
    assert result["selected_strategy"] == "COMPRESS"
    assert len(expert["fired_rules"]) > 0

    for rule in expert["fired_rules"]:
        assert "rule_id" in rule
        assert "strategy" in rule


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
    print("SKILLSPRINT CI INTEGRATION TEST")
    print("=" * 60)
    print()
    print("STEP 1 - FUZZY LOGIC")
    print(
        "Time availability ratio:",
        round(result["fuzzy"]["time_availability_ratio"], 3),
    )
    print("Progress ratio:", result["fuzzy"]["progress_ratio"])
    print(
        "Workload adjustment:",
        round(result["fuzzy"]["crisp_adjustment"], 4),
    )
    print()
    print("STEP 2 - EXPERT SYSTEM")
    print("Selected strategy:", result["selected_strategy"])
    print()
    print("Fired rules:")
    for rule in result["expert"]["fired_rules"]:
        print(f"  {rule['rule_id']} -> {rule['strategy']}")
    print()
    print("STEP 3 - CI DECISION")
    print("Fuzzy + Expert System integration successful.")
    print()
    print("=" * 60)