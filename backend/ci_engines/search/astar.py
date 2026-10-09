import heapq


class AStarSearch:
    def __init__(
        self,
        graph,
        topics,
        cost_calculator,
        heuristic_calculator,
        node_limit=20000
    ):
        self.graph = graph

        self.topics = {
            topic["id"]: topic
            for topic in topics
        }

        self.cost_calculator = cost_calculator
        self.heuristic_calculator = heuristic_calculator
        self.node_limit = node_limit

    def search(
        self,
        selected_topics,
        completed_topics=None,
        daily_capacity=120
    ):
        selected_topics = set(selected_topics)
        completed_topics = set(completed_topics or set())

        remaining_topics = selected_topics - completed_topics

        if not remaining_topics:
            return {
                "success": True,
                "sequence": [],
                "cost": 0.0,
                "nodes_expanded": 0
            }

        start_state = tuple(sorted(completed_topics))

        initial_heuristic = self.heuristic_calculator.estimate(
            remaining_topics,
            daily_capacity
        )

        queue = []

        heapq.heappush(
            queue,
            (
                initial_heuristic,
                0.0,
                start_state,
                None
            )
        )

        best_cost = {
            start_state: 0.0
        }

        parent = {
            start_state: None
        }

        action = {
            start_state: None
        }

        nodes_expanded = 0

        while queue and nodes_expanded < self.node_limit:
            f_score, current_cost, state, previous_topic_id = heapq.heappop(
                queue
            )

            if current_cost > best_cost.get(state, float("inf")):
                continue

            nodes_expanded += 1

            completed = set(state)

            remaining = selected_topics - completed

            if not remaining:
                sequence = self._reconstruct_path(
                    state,
                    parent,
                    action
                )

                return {
                    "success": True,
                    "sequence": sequence,
                    "cost": current_cost,
                    "nodes_expanded": nodes_expanded
                }

            available_topics = self.graph.get_available_topics(
                completed_topics=completed,
                selected_topics=remaining
            )

            for topic_id in available_topics:
                topic = self.topics[topic_id]

                previous_topic = None

                if previous_topic_id is not None:
                    previous_topic = self.topics.get(
                        previous_topic_id
                    )

                expected_position = len(completed) + 1

                step_cost = self.cost_calculator.topic_cost(
                    current_topic=topic,
                    previous_topic=previous_topic,
                    expected_position=expected_position
                )

                new_cost = current_cost + step_cost

                new_state = tuple(
                    sorted(
                        completed | {topic_id}
                    )
                )

                if new_cost >= best_cost.get(
                    new_state,
                    float("inf")
                ):
                    continue

                best_cost[new_state] = new_cost

                parent[new_state] = state
                action[new_state] = topic_id

                new_remaining = selected_topics - set(new_state)

                heuristic = self.heuristic_calculator.estimate(
                    new_remaining,
                    daily_capacity
                )

                new_f_score = new_cost + heuristic

                heapq.heappush(
                    queue,
                    (
                        new_f_score,
                        new_cost,
                        new_state,
                        topic_id
                    )
                )

        return {
            "success": False,
            "sequence": [],
            "cost": None,
            "nodes_expanded": nodes_expanded,
            "reason": "Search limit reached or no valid roadmap found"
        }

    def _reconstruct_path(
        self,
        state,
        parent,
        action
    ):
        sequence = []

        current_state = state

        while parent[current_state] is not None:
            topic_id = action[current_state]

            sequence.append(topic_id)

            current_state = parent[current_state]

        sequence.reverse()

        return sequence