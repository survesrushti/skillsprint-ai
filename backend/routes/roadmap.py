from datetime import date

from flask import Blueprint, jsonify, request

from extensions import db
from models import Goal, Roadmap, RoadmapItem, Topic, TopicPrerequisite
from ci_engines.rescheduler.engine import Rescheduler


roadmap_bp = Blueprint(
    "roadmap",
    __name__,
    url_prefix="/api/v1/roadmap"
)


@roadmap_bp.post("/generate")
def generate_roadmap():
    data = request.get_json(silent=True) or {}

    goal_id = data.get("goal_id")

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id is required."
        }), 400

    try:
        goal = db.session.get(
            Goal,
            int(goal_id)
        )

        if goal is None:
            return jsonify({
                "status": "error",
                "message": "Goal not found."
            }), 404

        topics = Topic.query.filter_by(
            track_id=goal.track_id
        ).order_by(
            Topic.id
        ).all()

        if not topics:
            return jsonify({
                "status": "error",
                "message": "No topics found for this learning track."
            }), 404

        topic_ids = {
            topic.id
            for topic in topics
        }

        prerequisite_rows = TopicPrerequisite.query.filter(
            TopicPrerequisite.topic_id.in_(topic_ids),
            TopicPrerequisite.prerequisite_topic_id.in_(topic_ids)
        ).all()

        search_topics = []

        for topic in topics:
            search_topics.append({
                "id": topic.id,
                "name": topic.name,
                "estimated_minutes": topic.estimated_minutes,
                "difficulty": topic.difficulty,
                "priority": topic.priority,
                "is_optional": topic.is_optional
            })

        prerequisites = [
            (
                row.topic_id,
                row.prerequisite_topic_id
            )
            for row in prerequisite_rows
        ]

        selected_topics = {
            topic.id
            for topic in topics
            if not topic.is_optional
        }

        completed_topics = set()

        required_minutes = sum(
            topic.estimated_minutes
            for topic in topics
            if not topic.is_optional
        )

        study_hours = float(
            goal.study_hours_per_day
        )

        daily_capacity = int(
            study_hours * 60
        )

        days_remaining = (
            goal.target_date - date.today()
        ).days + 1

        if days_remaining < 1:
            days_remaining = 1

        available_minutes = (
            days_remaining * daily_capacity
        )

        progress_ratio = 0.0

        optional_topics_remaining = sum(
            1
            for topic in topics
            if topic.is_optional
        )

        rescheduler = Rescheduler()

        result = rescheduler.evaluate(
            progress_ratio=progress_ratio,
            available_minutes=available_minutes,
            required_minutes=required_minutes,
            missed_days=0,
            backlog_minutes=0,
            optional_topics_remaining=optional_topics_remaining,
            current_streak=0,
            recent_replans=0,
            days_remaining=days_remaining,
            topics=search_topics,
            prerequisites=prerequisites,
            selected_topics=selected_topics,
            completed_topics=completed_topics,
            study_hours_per_day=study_hours
        )

        search_result = result.get("search")

        if not search_result:
            return jsonify({
                "status": "error",
                "message": "Roadmap search did not return a result.",
                "ci": {
                    "fuzzy": result.get("fuzzy"),
                    "expert": result.get("expert")
                }
            }), 500

        if not search_result.get("success"):
            return jsonify({
                "status": "error",
                "message": search_result.get(
                    "message",
                    "Could not generate roadmap."
                ),
                "ci": {
                    "fuzzy": result.get("fuzzy"),
                    "expert": result.get("expert"),
                    "search": search_result
                }
            }), 422

        topic_lookup = {
            topic.id: topic
            for topic in topics
        }

        daily_plan = []

        for index, day in enumerate(
            search_result.get(
                "daily_plan",
                []
            ),
            start=1
        ):
            day_tasks = []

            for task in day.get(
                "tasks",
                []
            ):
                topic_id = task.get("topic_id")

                topic = topic_lookup.get(
                    topic_id
                )

                if topic is None:
                    continue

                minutes = task.get(
                    "minutes",
                    0
                )

                day_tasks.append({
                    "topic_id": topic.id,
                    "name": topic.name,
                    "minutes": minutes,
                    "difficulty": topic.difficulty,
                    "is_optional": topic.is_optional
                })

            daily_plan.append({
                "day": day.get("day") or index,
                "total_minutes": sum(
                    task["minutes"]
                    for task in day_tasks
                ),
                "tasks": day_tasks
            })

        # ------------------------------------------------------------
        # SAVE THE ROADMAP TO MYSQL
        # Each call creates a new version. Older active versions for
        # this goal are marked "superseded" so history is kept.
        # ------------------------------------------------------------
        try:
            latest_version = db.session.query(
                db.func.max(Roadmap.version_number)
            ).filter(
                Roadmap.goal_id == goal.id
            ).scalar()

            next_version = (latest_version or 0) + 1

            db.session.query(Roadmap).filter(
                Roadmap.goal_id == goal.id,
                Roadmap.status == "active"
            ).update(
                {"status": "superseded"},
                synchronize_session=False
            )

            roadmap = Roadmap(
                goal_id=goal.id,
                version_number=next_version,
                status="active"
            )

            db.session.add(roadmap)
            db.session.flush()  # gives roadmap.id before the commit

            items = []

            for day in daily_plan:
                for task in day["tasks"]:
                    items.append(
                        RoadmapItem(
                            roadmap_id=roadmap.id,
                            topic_id=task["topic_id"],
                            day_number=int(day["day"]),
                            planned_minutes=int(
                                round(task["minutes"])
                            ),
                            status="pending"
                        )
                    )

            db.session.add_all(items)
            db.session.commit()

            saved_roadmap_id = roadmap.id
            saved_roadmap_version = roadmap.version_number
            saved_item_count = len(items)

        except Exception as save_error:
            db.session.rollback()

            return jsonify({
                "status": "error",
                "message": "Roadmap was generated but could not be saved.",
                "error": str(save_error)
            }), 500

        return jsonify({
            "status": "success",
            "message": "Personalized roadmap generated successfully.",

            "roadmap_id": saved_roadmap_id,
            "roadmap_version": saved_roadmap_version,
            "items_saved": saved_item_count,

            "goal": {
                "id": goal.id,
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime(
                    "%d/%m/%Y"
                ),
                "known_topics": (
                    goal.known_topics.split(",")
                    if goal.known_topics
                    else []
                )
            },

            "ci": {
                "fuzzy": result.get("fuzzy"),
                "expert": result.get("expert"),

                "search": {
                    "success": search_result.get(
                        "success"
                    ),
                    "sequence": search_result.get(
                        "sequence",
                        []
                    ),
                    "total_minutes": search_result.get(
                        "total_minutes",
                        0
                    ),
                    "daily_capacity": search_result.get(
                        "daily_capacity",
                        daily_capacity
                    ),
                    "total_days": search_result.get(
                        "total_days",
                        len(daily_plan)
                    ),
                    "search_cost": search_result.get(
                        "search_cost"
                    ),
                    "nodes_expanded": search_result.get(
                        "nodes_expanded"
                    )
                }
            },

            "roadmap": daily_plan
        }), 200

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "goal_id must be a valid number."
        }), 400

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Could not generate roadmap.",
            "error": str(error)
        }), 500