def triangular_membership(
    value,
    left,
    center,
    right
):
    if value <= left:
        return 0.0

    if value == center:
        return 1.0

    if value >= right:
        return 0.0

    if value < center:
        return (value - left) / (center - left)

    return (right - value) / (right - center)


def left_shoulder_membership(
    value,
    start,
    end
):
    if value <= start:
        return 1.0

    if value >= end:
        return 0.0

    return (end - value) / (end - start)


def right_shoulder_membership(
    value,
    start,
    end
):
    if value <= start:
        return 0.0

    if value >= end:
        return 1.0

    return (value - start) / (end - start)


def clip(value):
    return max(0.0, min(1.0, value))