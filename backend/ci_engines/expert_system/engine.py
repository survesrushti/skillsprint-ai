from .facts import LearningFacts
from .rules import get_rules_by_priority
from .strategies import get_strategy
from .trace import ExplanationTrace


class ExpertSystem:

    def __init__(self):
        self.rules = get_rules_by_priority()
        self.trace_generator = ExplanationTrace()

    def evaluate(self, facts):
        derived_facts = self._classify_facts(facts)

        fired_rules = []

        for rule in self.rules:
            if self._condition_matches(
                rule["condition"],
                derived_facts
            ):
                fired_rules.append({
                    "rule_id": rule["id"],
                    "condition": rule["condition"],
                    "strategy": rule["strategy"],
                    "priority": rule["priority"],
                    "reason": rule["reason"]
                })

        selected_strategy = self._select_strategy(
            fired_rules
        )

        strategy_details = get_strategy(
            selected_strategy
        )

        trace = self.trace_generator.create(
            facts=facts.to_dict(),
            derived_facts=derived_facts,
            fired_rules=fired_rules,
            selected_strategy=selected_strategy,
            strategy=strategy_details
        )

        return {
            "facts": facts.to_dict(),
            "derived_facts": derived_facts,
            "fired_rules": fired_rules,
            "selected_strategy": selected_strategy,
            "strategy": strategy_details,
            "trace": trace
        }

    def _classify_facts(self, facts):
        classified = {}

        capacity_ratio = 0.0

        if facts.required_minutes > 0:
            capacity_ratio = (
                facts.available_minutes
                / facts.required_minutes
            )

        classified["critical_deadline"] = (
            facts.days_remaining <= 2
            and
            facts.required_minutes
            > facts.available_minutes
        )

        classified["severe_backlog"] = (
            facts.backlog_minutes >= 180
        )

        classified["behind_and_missed"] = (
            facts.progress_ratio < 0.8
            and
            facts.missed_days > 0
        )

        classified["behind"] = (
            facts.progress_ratio < 0.8
        )

        classified["fuzzy_large_increase"] = (
            facts.fuzzy_adjustment >= 0.20
        )

        classified["optional_topics_and_backlog"] = (
            facts.optional_topics_remaining > 0
            and
            facts.backlog_minutes > 0
        )

        classified["long_absence"] = (
            facts.missed_days >= 3
        )

        classified["ahead"] = (
            facts.progress_ratio > 1.2
        )

        classified["high_streak"] = (
            facts.current_streak >= 7
        )

        classified["recent_replans"] = (
            facts.recent_replans >= 3
        )

        classified["ample_capacity"] = (
            capacity_ratio >= 1.5
        )

        classified["on_track"] = (
            0.8 <= facts.progress_ratio <= 1.2
        )

        classified["no_missed_sessions"] = (
            facts.missed_days == 0
        )

        return classified

    def _condition_matches(
        self,
        condition,
        derived_facts
    ):
        return derived_facts.get(
            condition,
            False
        )

    def _select_strategy(
        self,
        fired_rules
    ):
        if not fired_rules:
            return "NO_CHANGE"

        return fired_rules[0]["strategy"]