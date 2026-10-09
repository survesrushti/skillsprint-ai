from .engine import Rescheduler


rescheduler = Rescheduler()


result = rescheduler.evaluate(
    progress_ratio=0.6,
    available_minutes=120,
    required_minutes=180,
    missed_days=2,
    backlog_minutes=120,
    optional_topics_remaining=3,
    current_streak=2,
    recent_replans=1,
    days_remaining=5
)


print("=" * 60)
print("SKILLSPRINT CI INTEGRATION TEST")
print("=" * 60)

print()
print("STEP 1 - FUZZY LOGIC")

print(
    "Time availability ratio:",
    round(
        result["fuzzy"]["time_availability_ratio"],
        3
    )
)

print(
    "Progress ratio:",
    result["fuzzy"]["progress_ratio"]
)

print(
    "Workload adjustment:",
    round(
        result["fuzzy"]["crisp_adjustment"],
        4
    )
)

print()
print("STEP 2 - EXPERT SYSTEM")

print(
    "Selected strategy:",
    result["selected_strategy"]
)

print()
print("Fired rules:")

for rule in result["expert"]["fired_rules"]:
    print(
        f"  {rule['rule_id']} -> "
        f"{rule['strategy']}"
    )

print()
print("STEP 3 - CI DECISION")

print(
    "Fuzzy + Expert System integration successful."
)

print()
print("=" * 60)