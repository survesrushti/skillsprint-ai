from heuristic import HeuristicCalculator


topics = [
    {
        "id": 1,
        "name": "HTML",
        "estimated_minutes": 60
    },
    {
        "id": 2,
        "name": "CSS",
        "estimated_minutes": 90
    },
    {
        "id": 3,
        "name": "JavaScript",
        "estimated_minutes": 120
    }
]


calculator = HeuristicCalculator(topics)


remaining_topics = {2, 3}


print(
    "Remaining minutes:",
    calculator.remaining_minutes(remaining_topics)
)

print(
    "Minimum days required:",
    calculator.minimum_days_required(
        remaining_topics,
        daily_capacity=120
    )
)

print(
    "A* heuristic estimate:",
    calculator.estimate(
        remaining_topics,
        daily_capacity=120
    )
)