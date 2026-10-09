class ExplanationTrace:

    def create(
        self,
        facts,
        derived_facts,
        fired_rules,
        selected_strategy,
        strategy
    ):
        trace = []

        trace.append({
            "step": 1,
            "type": "facts",
            "message": (
                "Learner information was collected "
                "for the current roadmap."
            ),
            "data": facts
        })

        active_facts = [
            name
            for name, value in derived_facts.items()
            if value
        ]

        trace.append({
            "step": 2,
            "type": "classification",
            "message": (
                "The Expert System classified "
                "the learner's current situation."
            ),
            "active_facts": active_facts
        })

        for rule in fired_rules:
            trace.append({
                "step": len(trace) + 1,
                "type": "rule",
                "rule_id": rule["rule_id"],
                "condition": rule["condition"],
                "message": rule["reason"],
                "strategy": rule["strategy"],
                "priority": rule["priority"]
            })

        trace.append({
            "step": len(trace) + 1,
            "type": "decision",
            "message": (
                f"The Expert System selected "
                f"{selected_strategy}."
            ),
            "strategy": selected_strategy,
            "description": strategy["description"]
        })

        return trace