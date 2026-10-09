from packer import StudyPlanPacker


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
    },
    {
        "id": 4,
        "name": "React",
        "estimated_minutes": 150
    }
]


packer = StudyPlanPacker(topics)


topic_sequence = [1, 2, 3, 4]


daily_capacity = 120


days = packer.pack(
    topic_sequence=topic_sequence,
    daily_capacity=daily_capacity
)


print("Generated study plan:")
print()


for day in days:
    print(f"Day {day['day']}:")

    for task in day["tasks"]:
        print(
            f"  {task['topic_name']}: "
            f"{task['minutes']} minutes"
        )

    print()


print(
    "Total planned minutes:",
    packer.total_planned_minutes(days)
)