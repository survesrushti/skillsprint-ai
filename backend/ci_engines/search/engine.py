from .graph import TopicGraph
from .capacity import CapacityCalculator
from .cost import CostCalculator
from .heuristic import HeuristicCalculator
from .astar import AStarSearch
from .packer import StudyPlanPacker


class SearchEngine:
    def generate_roadmap(
        self,
        topics,
        prerequisites,
        selected_topics,
        completed_topics=None,
        study_hours_per_day=2
    ):
        completed_topics = set(completed_topics or set())

        selected_topics = set(selected_topics)

        if not selected_topics:
            return {
                "success": False,
                "message": "No topics selected.",
                "sequence": [],
                "daily_plan": []
            }

        graph = TopicGraph(
            topics=topics,
            prerequisites=prerequisites
        )

        if not graph.validate():
            return {
                "success": False,
                "message": "Topic graph is invalid.",
                "sequence": [],
                "daily_plan": []
            }

        capacity = CapacityCalculator(
            study_hours_per_day=study_hours_per_day
        )

        daily_capacity = capacity.daily_capacity()

        cost_calculator = CostCalculator()

        heuristic_calculator = HeuristicCalculator(
            topics=topics,
            cost_calculator=cost_calculator
        )

        astar = AStarSearch(
            graph=graph,
            topics=topics,
            cost_calculator=cost_calculator,
            heuristic_calculator=heuristic_calculator
        )

        search_result = astar.search(
            selected_topics=selected_topics,
            completed_topics=completed_topics,
            daily_capacity=daily_capacity
        )

        if not search_result["success"]:
            return {
                "success": False,
                "message": search_result.get(
                    "reason",
                    "Could not generate roadmap."
                ),
                "sequence": [],
                "daily_plan": [],
                "nodes_expanded": search_result.get(
                    "nodes_expanded",
                    0
                )
            }

        packer = StudyPlanPacker(
            topics=topics
        )

        daily_plan = packer.pack(
            topic_sequence=search_result["sequence"],
            daily_capacity=daily_capacity
        )

        total_minutes = packer.total_planned_minutes(
            daily_plan
        )

        return {
            "success": True,
            "message": "Roadmap generated successfully.",
            "sequence": search_result["sequence"],
            "daily_plan": daily_plan,
            "total_minutes": total_minutes,
            "daily_capacity": daily_capacity,
            "total_days": len(daily_plan),
            "search_cost": search_result["cost"],
            "nodes_expanded": search_result["nodes_expanded"]
        }