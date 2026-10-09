class MamdaniInference:

    def __init__(self, rules):
        self.rules = rules

    def evaluate(
        self,
        time_memberships,
        progress_memberships
    ):
        fired_rules = []

        for index, rule in enumerate(
            self.rules,
            start=1
        ):
            time_strength = time_memberships.get(
                rule["time"],
                0.0
            )

            progress_strength = progress_memberships.get(
                rule["progress"],
                0.0
            )

            firing_strength = min(
                time_strength,
                progress_strength
            )

            fired_rules.append({
                "rule_number": index,
                "time": rule["time"],
                "progress": rule["progress"],
                "output": rule["output"],
                "time_strength": time_strength,
                "progress_strength": progress_strength,
                "firing_strength": firing_strength
            })

        output_strengths = {}

        for rule in fired_rules:
            output = rule["output"]
            strength = rule["firing_strength"]

            if output not in output_strengths:
                output_strengths[output] = strength
            else:
                output_strengths[output] = max(
                    output_strengths[output],
                    strength
                )

        return {
            "fired_rules": fired_rules,
            "output_strengths": output_strengths
        }