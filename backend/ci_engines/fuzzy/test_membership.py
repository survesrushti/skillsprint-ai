from membership import (
    triangular_membership,
    left_shoulder_membership,
    right_shoulder_membership,
    clip
)


print(
    "Triangular:",
    triangular_membership(
        value=5,
        left=0,
        center=5,
        right=10
    )
)

print(
    "Left shoulder:",
    left_shoulder_membership(
        value=2,
        start=0,
        end=10
    )
)

print(
    "Right shoulder:",
    right_shoulder_membership(
        value=8,
        start=0,
        end=10
    )
)

print(
    "Clip above 1:",
    clip(1.5)
)

print(
    "Clip below 0:",
    clip(-0.5)
)