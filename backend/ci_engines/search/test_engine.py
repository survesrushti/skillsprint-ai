from engine import SearchEngine


topics = [
    {
        "id": 1,
        "name": "HTML",
        "estimated_minutes": 60,
        "difficulty": 1,
        "priority": 1.0,
        "canonical_position": 1
    },
    {
        "id": 2,
        "name": "CSS",
        "estimated_minutes": 90,
        "difficulty": 2,
        "priority": 1.2,
        "canonical_position": 2
    },
    {
        "id": 3,
        "name": "JavaScript",
        "estimated_minutes": 120,
        "difficulty": 3,
        "priority": 1.5,
        "canonical_position": 3
    },
    {
        "id": 4,
        "name": "React",
        "estimated_minutes": 150,
        "difficulty": 4,
        "priority": 1.4,
        "canonical_position": 4
    }
]


prerequisites = [
    (2, 1),
    (3, 2),
    (4, 3)
]


engine = SearchEngine()


result = engine.generate_roadmap(
    topics=topics,
    prerequisites=prerequisites,
    selected_topics={1, 2, 3, 4},
    completed_topics=set(),
    study_hours_per_day=2
)


print("Success:", result["success"])
print("Message:", result["message"])
print("Sequence:", result["sequence"])
print("Total minutes:", result["total_minutes"])
print("Daily capacity:", result["daily_capacity"])
print("Total days:", result["total_days"])
print("Search cost:", result["search_cost"])
print("Nodes expanded:", result["nodes_expanded"])

print()
print("Daily Roadmap:")

topic_names = {
    topic["id"]: topic["name"]
    for topic in topics
}

for day in result["daily_plan"]:
    print(f"\nDay {day['day']}:")

    for task in day["tasks"]:
        print(
            f"  {task['topic_name']}: "
            f"{task['minutes']} minutes"
        )