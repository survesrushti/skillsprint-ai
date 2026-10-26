import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from ci_engines.search.graph import TopicGraph


def test_topic_graph():
    topics = [
        {"id": 1, "name": "HTML"},
        {"id": 2, "name": "CSS"},
        {"id": 3, "name": "JavaScript"},
        {"id": 4, "name": "React"},
    ]

    prerequisites = [
        (2, 1),
        (3, 2),
        (4, 3),
    ]

    graph = TopicGraph(topics=topics, prerequisites=prerequisites)

    assert graph.validate() is True
    assert graph.get_prerequisites(2) == {1}
    assert graph.get_prerequisites(3) == {2}
    assert graph.get_prerequisites(4) == {3}

    available_after_1 = graph.get_available_topics(
        completed_topics={1},
        selected_topics={1, 2, 3, 4},
    )
    assert available_after_1 == [2]

    available_after_1_2 = graph.get_available_topics(
        completed_topics={1, 2},
        selected_topics={1, 2, 3, 4},
    )
    assert available_after_1_2 == [3]


if __name__ == "__main__":
    topics = [
        {"id": 1, "name": "HTML"},
        {"id": 2, "name": "CSS"},
        {"id": 3, "name": "JavaScript"},
        {"id": 4, "name": "React"},
    ]
    prerequisites = [
        (2, 1),
        (3, 2),
        (4, 3),
    ]
    graph = TopicGraph(topics=topics, prerequisites=prerequisites)
    print("Graph valid:", graph.validate())
    print("Prerequisites of CSS:", graph.get_prerequisites(2))
    print("Prerequisites of JavaScript:", graph.get_prerequisites(3))
    print("Prerequisites of React:", graph.get_prerequisites(4))
    print(
        "Available after HTML:",
        graph.get_available_topics(
            completed_topics={1}, selected_topics={1, 2, 3, 4}
        ),
    )
    print(
        "Available after HTML + CSS:",
        graph.get_available_topics(
            completed_topics={1, 2}, selected_topics={1, 2, 3, 4}
        ),
    )