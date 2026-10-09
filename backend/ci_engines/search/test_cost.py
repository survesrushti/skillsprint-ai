from cost import CostCalculator


calculator = CostCalculator()


html = {
    "id": 1,
    "name": "HTML",
    "difficulty": 1,
    "priority": 1.0,
    "canonical_position": 1
}

css = {
    "id": 2,
    "name": "CSS",
    "difficulty": 2,
    "priority": 1.2,
    "canonical_position": 2
}

javascript = {
    "id": 3,
    "name": "JavaScript",
    "difficulty": 3,
    "priority": 1.5,
    "canonical_position": 3
}


print(
    "HTML cost:",
    calculator.topic_cost(
        html,
        previous_topic=None,
        expected_position=1
    )
)

print(
    "CSS cost:",
    calculator.topic_cost(
        css,
        previous_topic=html,
        expected_position=2
    )
)

print(
    "JavaScript cost:",
    calculator.topic_cost(
        javascript,
        previous_topic=css,
        expected_position=3
    )
)