from .variables import FuzzyVariables
from .rules import get_rules
from .inference import MamdaniInference


class FuzzyEngine:

    def __init__(self):
        self.variables = FuzzyVariables()

        self.inference = MamdaniInference(
            rules=get_rules()
        )

    def calculate(
        self,
        time_availability_ratio,
        progress_ratio
    ):
        time_memberships = self.variables.time_availability(
            time_availability_ratio
        )

        progress_memberships = self.variables.progress(
            progress_ratio
        )

        inference_result = self.inference.evaluate(
            time_memberships=time_memberships,
            progress_memberships=progress_memberships
        )

        output_strengths = inference_result[
            "output_strengths"
        ]

        crisp_adjustment = self._defuzzify(
            output_strengths
        )

        return {
            "time_availability_ratio": time_availability_ratio,
            "progress_ratio": progress_ratio,
            "time_memberships": time_memberships,
            "progress_memberships": progress_memberships,
            "fired_rules": inference_result["fired_rules"],
            "output_strengths": output_strengths,
            "crisp_adjustment": crisp_adjustment
        }

    def _defuzzify(
        self,
        output_strengths,
        step=0.01
    ):
        numerator = 0.0
        denominator = 0.0

        x = -0.4

        while x <= 0.4:
            membership = self._aggregated_output_membership(
                x,
                output_strengths
            )

            numerator += x * membership
            denominator += membership

            x += step

        if denominator == 0:
            return 0.0

        result = numerator / denominator

        return max(
            -0.4,
            min(0.4, result)
        )

    def _aggregated_output_membership(
        self,
        value,
        output_strengths
    ):
        memberships = []

        memberships.append(
            min(
                output_strengths.get(
                    "LargeDecrease",
                    0.0
                ),
                self._left_shoulder(
                    value,
                    -0.4,
                    -0.2
                )
            )
        )

        memberships.append(
            min(
                output_strengths.get(
                    "SmallDecrease",
                    0.0
                ),
                self._triangle(
                    value,
                    -0.3,
                    -0.15,
                    0.0
                )
            )
        )

        memberships.append(
            min(
                output_strengths.get(
                    "NoChange",
                    0.0
                ),
                self._triangle(
                    value,
                    -0.05,
                    0.0,
                    0.05
                )
            )
        )

        memberships.append(
            min(
                output_strengths.get(
                    "SmallIncrease",
                    0.0
                ),
                self._triangle(
                    value,
                    0.0,
                    0.15,
                    0.3
                )
            )
        )

        memberships.append(
            min(
                output_strengths.get(
                    "LargeIncrease",
                    0.0
                ),
                self._right_shoulder(
                    value,
                    0.2,
                    0.4
                )
            )
        )

        return max(memberships)

    def _triangle(
        self,
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
            return (
                (value - left)
                / (center - left)
            )

        return (
            (right - value)
            / (right - center)
        )

    def _left_shoulder(
        self,
        value,
        start,
        end
    ):
        if value <= start:
            return 1.0

        if value >= end:
            return 0.0

        return (
            (end - value)
            / (end - start)
        )

    def _right_shoulder(
        self,
        value,
        start,
        end
    ):
        if value <= start:
            return 0.0

        if value >= end:
            return 1.0

        return (
            (value - start)
            / (end - start)
        )