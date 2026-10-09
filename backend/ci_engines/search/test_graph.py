from graph import TopicGraph


topics = [
    {
        "id": 1,
        "name": "HTML",
    },
    {
        "id": 2,
        "name": "CSS",
    },
    {
        "id": 3,
        "name": "JavaScript",
    },
    {
        "id": 4,
        "name": "React",
    },
]


prerequisites = [
    (2, 1),
    (3, 2),
    (4, 3),
]


graph = TopicGraph(
    topics=topics,
    prerequisites=prerequisites
)


print("Graph valid:", graph.validate())

print("Prerequisites of CSS:", graph.get_prerequisites(2))
print("Prerequisites of JavaScript:", graph.get_prerequisites(3))
print("Prerequisites of React:", graph.get_prerequisites(4))

print(
    "Available after HTML:",
    graph.get_available_topics(
        completed_topics={1},
        selected_topics={1, 2, 3, 4}
    )
)

print(
    "Available after HTML + CSS:",
    graph.get_available_topics(
        completed_topics={1, 2},
        selected_topics={1, 2, 3, 4}
    )
)