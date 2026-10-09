class StudyPlanPacker:
    def __init__(self, topics):
        self.topics = {
            topic["id"]: topic
            for topic in topics
        }

    def pack(
        self,
        topic_sequence,
        daily_capacity
    ):
        if daily_capacity <= 0:
            raise ValueError(
                "Daily capacity must be greater than zero."
            )

        days = []
        current_day = []
        remaining_capacity = daily_capacity
        day_number = 1

        for topic_id in topic_sequence:
            if topic_id not in self.topics:
                raise ValueError(
                    f"Topic {topic_id} was not found."
                )

            topic = self.topics[topic_id]
            remaining_minutes = topic.get(
                "estimated_minutes",
                0
            )

            if remaining_minutes <= 0:
                continue

            while remaining_minutes > 0:
                if remaining_capacity == 0:
                    days.append({
                        "day": day_number,
                        "tasks": current_day
                    })

                    day_number += 1
                    current_day = []
                    remaining_capacity = daily_capacity

                allocated_minutes = min(
                    remaining_minutes,
                    remaining_capacity
                )

                current_day.append({
                    "topic_id": topic_id,
                    "topic_name": topic["name"],
                    "minutes": allocated_minutes
                })

                remaining_minutes -= allocated_minutes
                remaining_capacity -= allocated_minutes

        if current_day:
            days.append({
                "day": day_number,
                "tasks": current_day
            })

        return days

    def total_planned_minutes(self, days):
        total = 0

        for day in days:
            for task in day["tasks"]:
                total += task["minutes"]

        return total