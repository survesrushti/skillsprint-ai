import sys
from pathlib import Path

CI_ENGINES_PATH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_ENGINES_PATH))

from fuzzy.engine import FuzzyEngine
from expert_system.engine import ExpertSystem
from expert_system.facts import LearningFacts
from search.engine import SearchEngine


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
        study_hours_per_day=2
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

        # STEP 3: SEARCH

        search_result = None

        if (
            topics is not None
            and prerequisites is not None
            and selected_topics is not None
        ):

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
            "selected_strategy": expert_result[
                "selected_strategy"
            ]
        }