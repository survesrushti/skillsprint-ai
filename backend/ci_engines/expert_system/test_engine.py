from facts import LearningFacts
from engine import ExpertSystem


facts = LearningFacts(
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


expert_system = ExpertSystem()

result = expert_system.evaluate(
    facts
)


print("Selected strategy:")
print("==================")
print(result["selected_strategy"])

print()

print("Explanation Trace:")
print("==================")

for step in result["trace"]:
    print(
        f"Step {step['step']}: "
        f"{step['message']}"
    )

    if step["type"] == "rule":
        print(
            f"  Rule: {step['rule_id']}"
        )

        print(
            f"  Strategy: {step['strategy']}"
        )

        print(
            f"  Priority: {step['priority']}"
        )

print()

print("Final explanation:")
print("==================")

for step in result["trace"]:
    if step["type"] == "rule":
        print(
            f"- {step['rule_id']}: "
            f"{step['message']}"
        )

print()

print(
    "Decision:",
    result["selected_strategy"]
)

print(
    "Description:",
    result["strategy"]["description"]
)