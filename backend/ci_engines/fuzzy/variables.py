from .membership import (
    left_shoulder_membership,
    triangular_membership,
    right_shoulder_membership
)


class FuzzyVariables:

    def time_availability(self, value):
        value = max(0.0, min(2.0, value))

        return {
            "Scarce": left_shoulder_membership(
                value,
                0.0,
                0.8
            ),
            "Adequate": triangular_membership(
                value,
                0.5,
                1.0,
                1.5
            ),
            "Ample": right_shoulder_membership(
                value,
                1.2,
                2.0
            )
        }

    def progress(self, value):
        value = max(0.0, min(2.0, value))

        return {
            "Behind": left_shoulder_membership(
                value,
                0.0,
                0.8
            ),
            "OnTrack": triangular_membership(
                value,
                0.5,
                1.0,
                1.5
            ),
            "Ahead": right_shoulder_membership(
                value,
                1.2,
                2.0
            )
        }

    def workload_adjustment(self, value):
        value = max(-0.4, min(0.4, value))

        return {
            "LargeDecrease": left_shoulder_membership(
                value,
                -0.4,
                -0.2
            ),
            "SmallDecrease": triangular_membership(
                value,
                -0.3,
                -0.15,
                0.0
            ),
            "NoChange": triangular_membership(
                value,
                -0.05,
                0.0,
                0.05
            ),
            "SmallIncrease": triangular_membership(
                value,
                0.0,
                0.15,
                0.3
            ),
            "LargeIncrease": right_shoulder_membership(
                value,
                0.2,
                0.4
            )
        }