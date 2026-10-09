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
print("RESCHEDULER TEST")
print("=" * 60)

print()
print("Fuzzy workload adjustment:")
print(
    result["fuzzy"]["crisp_adjustment"]
)

print()
print("Expert System strategy:")
print(
    result["selected_strategy"]
)

print()
print("Fired Expert System rules:")

for rule in result["expert"]["fired_rules"]:
    print(
        f"  {rule['rule_id']} -> "
        f"{rule['strategy']}"
    )

print()
print("Rescheduler test completed.")