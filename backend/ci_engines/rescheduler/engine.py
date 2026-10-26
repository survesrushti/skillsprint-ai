import sys
from pathlib import Path

CI_ENGINES_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_ENGINES_PATH))

from fuzzy.engine import FuzzyEngine
from expert_system.engine import ExpertSystem
from expert_system.facts import LearningFacts
from search.engine import SearchEngine
from search.packer import StudyPlanPacker


# How far the fuzzy adjustment may change the daily workload.
COMPRESS_MIN_INCREASE = 0.05
COMPRESS_MAX_INCREASE = 0.40
RELAX_MAX_DECREASE = 0.30
RELAX_SAFETY_MARGIN = 1.02


class Rescheduler:

    def __init__(self):
        self.fuzzy_engine = FuzzyEngine()
        self.expert_system = ExpertSystem()
        self.search_engine = SearchEngine()

    def evaluate(
        self,
        progress_ratio,
        available_minutes,
        required_minutes,
        missed_days=0,
        backlog_minutes=0,
        optional_topics_remaining=0,
        current_streak=0,
        recent_replans=0,
        days_remaining=7,
        topics=None,
        prerequisites=None,
        selected_topics=None,
        completed_topics=None,
        study_hours_per_day=2,
        apply_strategy=False
    ):

        time_availability_ratio = 0.0

        if required_minutes > 0:
            time_availability_ratio = (
                available_minutes / required_minutes
            )

        # STEP 1: FUZZY LOGIC

        fuzzy_result = self.fuzzy_engine.calculate(
            time_availability_ratio=time_availability_ratio,
            progress_ratio=progress_ratio
        )

        fuzzy_adjustment = fuzzy_result["crisp_adjustment"]

        # STEP 2: EXPERT SYSTEM

        facts = LearningFacts(
            progress_ratio=progress_ratio,
            available_minutes=available_minutes,
            required_minutes=required_minutes,
            missed_days=missed_days,
            backlog_minutes=backlog_minutes,
            optional_topics_remaining=optional_topics_remaining,
            current_streak=current_streak,
            recent_replans=recent_replans,
            fuzzy_adjustment=fuzzy_adjustment,
            days_remaining=days_remaining
        )

        expert_result = self.expert_system.evaluate(
            facts
        )

        selected_strategy = expert_result["selected_strategy"]

        # STEP 3: SEARCH

        search_result = None
        adaptation = None

        if (
            topics is not None
            and prerequisites is not None
            and selected_topics is not None
        ):

            if apply_strategy:
                # The strategy and the fuzzy adjustment change the plan.
                adaptation = self._plan_adaptation(
                    strategy_id=selected_strategy,
                    fuzzy_adjustment=fuzzy_adjustment,
                    study_hours_per_day=study_hours_per_day,
                    required_minutes=required_minutes,
                    available_minutes=available_minutes
                )

                search_result = self._search_with_adaptation(
                    topics=topics,
                    prerequisites=prerequisites,
                    selected_topics=selected_topics,
                    completed_topics=completed_topics,
                    adaptation=adaptation
                )

            else:
                # Original behaviour (used by /generate).
                search_result = self.search_engine.generate_roadmap(
                    topics=topics,
                    prerequisites=prerequisites,
                    selected_topics=selected_topics,
                    completed_topics=completed_topics,
                    study_hours_per_day=study_hours_per_day
                )

        return {
            "fuzzy": fuzzy_result,
            "expert": expert_result,
            "search": search_result,
            "selected_strategy": selected_strategy,
            "adaptation": adaptation
        }

    # ----------------------------------------------------------------
    # Turn the expert strategy + fuzzy adjustment into search settings
    # ----------------------------------------------------------------

    def _plan_adaptation(
        self,
        strategy_id,
        fuzzy_adjustment,
        study_hours_per_day,
        required_minutes,
        available_minutes
    ):
        factor = 1.0
        defer_optional = False
        extend_deadline = False
        notes = []

        if strategy_id == "COMPRESS":
            increase = min(
                max(fuzzy_adjustment, COMPRESS_MIN_INCREASE),
                COMPRESS_MAX_INCREASE
            )
            factor = 1.0 + increase
            notes.append(
                f"Daily workload raised by {increase:.0%} "
                f"(fuzzy adjustment {fuzzy_adjustment:+.2f})."
            )

        elif strategy_id == "RELAX":
            decrease = min(
                max(-fuzzy_adjustment, 0.0),
                RELAX_MAX_DECREASE
            )
            wanted = 1.0 - decrease

            if available_minutes > 0:
                needed = min(
                    1.0,
                    required_minutes
                    / available_minutes
                    * RELAX_SAFETY_MARGIN
                )
            else:
                needed = 1.0

            factor = max(wanted, needed)

            notes.append(
                f"Daily workload set to {factor:.0%} of normal "
                f"(fuzzy adjustment {fuzzy_adjustment:+.2f}; "
                f"never below what the deadline needs)."
            )

        elif strategy_id == "DEFER_OPTIONAL":
            defer_optional = True
            notes.append(
                "Optional topics are planned after all required topics."
            )

        elif strategy_id == "EXTEND_DEADLINE":
            extend_deadline = True
            notes.append(
                "Committed pace kept; the target date moves if the "
                "plan ends after it."
            )

        elif strategy_id == "REDISTRIBUTE":
            notes.append(
                "Unfinished work is spread over the remaining days "
                "at the committed pace."
            )

        else:
            notes.append("Committed pace kept.")

        return {
            "strategy": strategy_id,
            "capacity_factor": round(factor, 4),
            "base_study_hours": study_hours_per_day,
            "effective_study_hours": round(
                study_hours_per_day * factor,
                4
            ),
            "defer_optional": defer_optional,
            "deferred_topic_ids": [],
            "extend_deadline": extend_deadline,
            "notes": notes
        }

    def _search_with_adaptation(
        self,
        topics,
        prerequisites,
        selected_topics,
        completed_topics,
        adaptation
    ):
        completed = set(completed_topics or set())
        hours = adaptation["effective_study_hours"]

        if adaptation["defer_optional"]:
            deferred = self._defer_optional(
                topics=topics,
                prerequisites=prerequisites,
                selected_topics=selected_topics,
                completed_topics=completed,
                study_hours=hours
            )

            if deferred is not None:
                result, deferred_ids = deferred
                adaptation["deferred_topic_ids"] = deferred_ids
                return result

            adaptation["notes"].append(
                "Nothing could be deferred, so all topics were "
                "planned together."
            )

        return self.search_engine.generate_roadmap(
            topics=topics,
            prerequisites=prerequisites,
            selected_topics=selected_topics,
            completed_topics=completed,
            study_hours_per_day=hours
        )

    def _defer_optional(
        self,
        topics,
        prerequisites,
        selected_topics,
        completed_topics,
        study_hours
    ):
        optional_ids = {
            topic["id"]
            for topic in topics
            if topic.get("is_optional")
        }

        selected = set(selected_topics)

        optional_remaining = (
            (selected & optional_ids) - completed_topics
        )

        required_remaining = (
            (selected - optional_remaining) - completed_topics
        )

        if not optional_remaining or not required_remaining:
            return None

        first = self.search_engine.generate_roadmap(
            topics=topics,
            prerequisites=prerequisites,
            selected_topics=selected - optional_remaining,
            completed_topics=completed_topics,
            study_hours_per_day=study_hours
        )

        if not first.get("success"):
            return None

        second = self.search_engine.generate_roadmap(
            topics=topics,
            prerequisites=prerequisites,
            selected_topics=optional_remaining,
            completed_topics=completed_topics | set(first["sequence"]),
            study_hours_per_day=study_hours
        )

        if not second.get("success"):
            return None

        sequence = list(first["sequence"]) + list(second["sequence"])

        packer = StudyPlanPacker(topics=topics)

        daily_plan = packer.pack(
            topic_sequence=sequence,
            daily_capacity=first["daily_capacity"]
        )

        combined = {
            "success": True,
            "message": "Roadmap generated successfully (optional topics deferred).",
            "sequence": sequence,
            "daily_plan": daily_plan,
            "total_minutes": packer.total_planned_minutes(daily_plan),
            "daily_capacity": first["daily_capacity"],
            "total_days": len(daily_plan),
            "search_cost": first["search_cost"] + second["search_cost"],
            "nodes_expanded": (
                first["nodes_expanded"] + second["nodes_expanded"]
            )
        }

        return combined, sorted(optional_remaining)