from facts import LearningFacts


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


print("Learning Facts")
print("================")

for name, value in facts.to_dict().items():
    print(f"{name}: {value}")