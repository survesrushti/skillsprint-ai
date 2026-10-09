class HeuristicCalculator:
    def __init__(self, topics):
        self.topics = {
            topic["id"]: topic
            for topic in topics
        }

    def remaining_minutes(self, remaining_topic_ids):
        total = 0

        for topic_id in remaining_topic_ids:
            topic = self.topics.get(topic_id)

            if topic:
                total += topic.get("estimated_minutes", 0)

        return total

    def minimum_days_required(
        self,
        remaining_topic_ids,
        daily_capacity
    ):
        if daily_capacity <= 0:
            return float("inf")

        minutes = self.remaining_minutes(
            remaining_topic_ids
        )

        if minutes == 0:
            return 0

        return (minutes + daily_capacity - 1) // daily_capacity

    def estimate(
        self,
        remaining_topic_ids,
        daily_capacity
    ):
        return self.remaining_minutes(
            remaining_topic_ids
        )