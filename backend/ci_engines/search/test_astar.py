from graph import TopicGraph
from cost import CostCalculator
from heuristic import HeuristicCalculator
from astar import AStarSearch


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


graph = TopicGraph(
    topics=topics,
    prerequisites=prerequisites
)


cost_calculator = CostCalculator()

heuristic_calculator = HeuristicCalculator(
    topics
)


search = AStarSearch(
    graph=graph,
    topics=topics,
    cost_calculator=cost_calculator,
    heuristic_calculator=heuristic_calculator
)


result = search.search(
    selected_topics={1, 2, 3, 4},
    completed_topics=set(),
    daily_capacity=120
)


print("Search successful:", result["success"])

print(
    "Topic sequence:",
    result["sequence"]
)

print(
    "Total cost:",
    result["cost"]
)

print(
    "Nodes expanded:",
    result["nodes_expanded"]
)


topic_names = {
    topic["id"]: topic["name"]
    for topic in topics
}


print(
    "Roadmap:",
    [
        topic_names[topic_id]
        for topic_id in result["sequence"]
    ]
)