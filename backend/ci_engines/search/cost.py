class CostCalculator:
    def __init__(self, difficulty_weight=2.0, sequence_weight=1.0):
        self.difficulty_weight = difficulty_weight
        self.sequence_weight = sequence_weight

    def priority_cost(self, topic):
        return float(topic.get("priority", 1.0))

    def minimum_step_cost(self, topic=None):
        if topic is None:
            return 1.0
        return self.priority_cost(topic)

    def difficulty_jump_cost(self, previous_topic, current_topic):
        if previous_topic is None:
            return 0.0

        previous_difficulty = previous_topic.get("difficulty", 1)
        current_difficulty = current_topic.get("difficulty", 1)

        jump = abs(current_difficulty - previous_difficulty)

        return jump * self.difficulty_weight

    def sequence_deviation_cost(self, current_topic, expected_position):
        current_position = current_topic.get(
            "canonical_position",
            expected_position
        )

        deviation = abs(current_position - expected_position)

        return deviation * self.sequence_weight

    def topic_cost(
        self,
        current_topic,
        previous_topic=None,
        expected_position=1
    ):
        priority = self.priority_cost(current_topic)

        difficulty = self.difficulty_jump_cost(
            previous_topic,
            current_topic
        )

        sequence = self.sequence_deviation_cost(
            current_topic,
            expected_position
        )

        total = priority + difficulty + sequence

        return total