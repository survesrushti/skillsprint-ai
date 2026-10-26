import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.expert_system.strategies import (
    get_strategy,
    get_all_strategies,
)


def test_expert_strategies():
    strategies = get_all_strategies()
    assert len(strategies) == 6
    expected_keys = {
        "NO_CHANGE",
        "REDISTRIBUTE",
        "COMPRESS",
        "DEFER_OPTIONAL",
        "EXTEND_DEADLINE",
        "RELAX",
    }
    assert set(strategies.keys()) == expected_keys

    for key, val in strategies.items():
        assert "name" in val
        assert "description" in val

    compress = get_strategy("COMPRESS")
    assert compress is not None
    assert compress["name"] == "Compress"
    assert compress["description"] == "Increase the workload to recover from a backlog."

    assert get_strategy("UNKNOWN_STRATEGY") is None


if __name__ == "__main__":
    print("Available strategies:")
    print("=====================")
    for strategy_id, strategy in get_all_strategies().items():
        print(f"{strategy_id}: {strategy['name']}")
    print()
    print("Selected strategy:")
    strategy = get_strategy("COMPRESS")
    print(f"Name: {strategy['name']}")
    print(f"Description: {strategy['description']}")