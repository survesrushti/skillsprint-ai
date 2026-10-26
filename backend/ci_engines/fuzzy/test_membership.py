import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.fuzzy.membership import (
    triangular_membership,
    left_shoulder_membership,
    right_shoulder_membership,
    clip,
)


def test_fuzzy_memberships():
    # Triangular
    assert triangular_membership(value=5, left=0, center=5, right=10) == 1.0
    assert triangular_membership(value=0, left=0, center=5, right=10) == 0.0
    assert triangular_membership(value=10, left=0, center=5, right=10) == 0.0
    assert triangular_membership(value=2.5, left=0, center=5, right=10) == 0.5
    assert triangular_membership(value=7.5, left=0, center=5, right=10) == 0.5

    # Left shoulder
    assert left_shoulder_membership(value=0, start=0, end=10) == 1.0
    assert left_shoulder_membership(value=-1, start=0, end=10) == 1.0
    assert left_shoulder_membership(value=2, start=0, end=10) == 0.8
    assert left_shoulder_membership(value=10, start=0, end=10) == 0.0
    assert left_shoulder_membership(value=12, start=0, end=10) == 0.0

    # Right shoulder
    assert right_shoulder_membership(value=0, start=0, end=10) == 0.0
    assert right_shoulder_membership(value=-2, start=0, end=10) == 0.0
    assert right_shoulder_membership(value=8, start=0, end=10) == 0.8
    assert right_shoulder_membership(value=10, start=0, end=10) == 1.0
    assert right_shoulder_membership(value=15, start=0, end=10) == 1.0

    # Clip
    assert clip(1.5) == 1.0
    assert clip(-0.5) == 0.0
    assert clip(0.4) == 0.4


if __name__ == "__main__":
    print(
        "Triangular:",
        triangular_membership(value=5, left=0, center=5, right=10),
    )
    print("Left shoulder:", left_shoulder_membership(value=2, start=0, end=10))
    print("Right shoulder:", right_shoulder_membership(value=8, start=0, end=10))
    print("Clip above 1:", clip(1.5))
    print("Clip below 0:", clip(-0.5))