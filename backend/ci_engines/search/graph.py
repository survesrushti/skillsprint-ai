class TopicGraph:
    def __init__(self, topics, prerequisites):
        self.topics = {
            topic["id"]: topic
            for topic in topics
        }

        self.prerequisites = {
            topic_id: set()
            for topic_id in self.topics
        }

        self.dependents = {
            topic_id: set()
            for topic_id in self.topics
        }

        for topic_id, prerequisite_id in prerequisites:
            self.prerequisites[topic_id].add(prerequisite_id)

            if prerequisite_id in self.dependents:
                self.dependents[prerequisite_id].add(topic_id)

    def get_prerequisites(self, topic_id):
        return self.prerequisites.get(topic_id, set())

    def get_dependents(self, topic_id):
        return self.dependents.get(topic_id, set())

    def get_available_topics(self, completed_topics, selected_topics):
        completed_topics = set(completed_topics)

        available = []

        for topic_id in selected_topics:
            if topic_id in completed_topics:
                continue

            required = self.get_prerequisites(topic_id)

            if required.issubset(completed_topics):
                available.append(topic_id)

        return sorted(available)

    def validate(self):
        for topic_id, prerequisites in self.prerequisites.items():
            for prerequisite_id in prerequisites:
                if prerequisite_id not in self.topics:
                    return False

        return True