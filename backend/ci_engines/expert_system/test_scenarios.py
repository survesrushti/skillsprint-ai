from facts import LearningFacts
from engine import ExpertSystem


expert_system = ExpertSystem()


scenarios = [
    {
        "name": "Behind + Missed Sessions",
        "facts": LearningFacts(
            progress_ratio=0.6,
            available_minutes=120,
            required_minutes=180,
            missed_days=2,
            backlog_minutes=120,
            optional_topics_remaining=3,
            current_streak=2,
            recent_replans=1,
            fuzzy_adjustment=0.2152,
            days_remaining=5
        )
    },
    {
        "name": "Ahead Learner",
        "facts": LearningFacts(
            progress_ratio=1.4,
            available_minutes=300,
            required_minutes=180,
            missed_days=0,
            backlog_minutes=0,
            optional_topics_remaining=2,
            current_streak=8,
            recent_replans=0,
            fuzzy_adjustment=-0.20,
            days_remaining=7
        )
    },
    {
        "name": "On Track",
        "facts": LearningFacts(
            progress_ratio=1.0,
            available_minutes=180,
            required_minutes=180,
            missed_days=0,
            backlog_minutes=0,
            optional_topics_remaining=0,
            current_streak=5,
            recent_replans=0,
            fuzzy_adjustment=0.0,
            days_remaining=7
        )
    },
    {
        "name": "Critical Deadline",
        "facts": LearningFacts(
            progress_ratio=0.5,
            available_minutes=60,
            required_minutes=300,
            missed_days=4,
            backlog_minutes=240,
            optional_topics_remaining=2,
            current_streak=0,
            recent_replans=1,
            fuzzy_adjustment=0.30,
            days_remaining=1
        )
    }
]


for scenario in scenarios:

    result = expert_system.evaluate(
        scenario["facts"]
    )

    print("=" * 60)

    print(
        "Scenario:",
        scenario["name"]
    )

    print(
        "Selected strategy:",
        result["selected_strategy"]
    )

    print()

    print("Fired rules:")

    for rule in result["fired_rules"]:
        print(
            f"  {rule['rule_id']} -> "
            f"{rule['strategy']} "
            f"(Priority {rule['priority']})"
        )

    print()