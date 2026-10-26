from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from extensions import db
from models import Goal, Roadmap, RoadmapItem, StudyLog, Topic
from routes.resources import get_item_resource
from middleware.auth import check_goal_access


tasks_bp = Blueprint(
    "tasks",
    __name__,
    url_prefix="/api/v1/tasks"
)


def _roadmap_start_date(roadmap):
    """
    Day 1 of a roadmap = the local calendar date it was created.
    created_at is stored in UTC, so convert it to local time first.
    """
    created = roadmap.created_at or datetime.utcnow()

    return created.replace(
        tzinfo=timezone.utc
    ).astimezone().date()


def _parse_date(text):
    return datetime.strptime(
        text,
        "%Y-%m-%d"
    ).date()


def _active_roadmap(goal_id):
    return Roadmap.query.filter_by(
        goal_id=goal_id,
        status="active"
    ).order_by(
        Roadmap.version_number.desc()
    ).first()


def _item_to_dict(item, topic_names, start_date):
    scheduled = start_date + timedelta(
        days=item.day_number - 1
    )

    resource, available = get_item_resource(item.id, item.topic_id)

    return {
        "id": item.id,
        "topic_id": item.topic_id,
        "topic_name": topic_names.get(
            item.topic_id,
            "Unknown topic"
        ),
        "day_number": item.day_number,
        "scheduled_date": scheduled.isoformat(),
        "planned_minutes": item.planned_minutes,
        "status": item.status,
        "resource": resource,
        "available_resources": available,
    }


@tasks_bp.get("/today")
def get_today_tasks():
    goal_id = request.args.get(
        "goal_id",
        type=int
    )

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id is required."
        }), 400

    date_text = request.args.get("date")

    try:
        today = (
            _parse_date(date_text)
            if date_text
            else date.today()
        )
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "date must look like YYYY-MM-DD."
        }), 400

    try:
        goal = db.session.get(Goal, goal_id)

        if goal is None:
            return jsonify({
                "status": "error",
                "message": "Goal not found."
            }), 404

        allowed, msg = check_goal_access(goal)
        if not allowed:
            code = 401 if ("Authentication required" in msg or "token" in msg.lower()) else 403
            return jsonify({
                "status": "error",
                "message": msg
            }), code

        roadmap = _active_roadmap(goal_id)

        if roadmap is None:
            return jsonify({
                "status": "error",
                "message": "No active roadmap. Generate one first."
            }), 404

        start_date = _roadmap_start_date(roadmap)

        items = RoadmapItem.query.filter_by(
            roadmap_id=roadmap.id
        ).order_by(
            RoadmapItem.day_number,
            RoadmapItem.id
        ).all()

        topic_names = {}

        if items:
            topic_ids = {
                item.topic_id
                for item in items
            }

            topic_names = {
                topic.id: topic.name
                for topic in Topic.query.filter(
                    Topic.id.in_(topic_ids)
                ).all()
            }

        total_days = max(
            (item.day_number for item in items),
            default=0
        )

        current_day = (today - start_date).days + 1

        if current_day < 1:
            plan_status = "not_started"
        elif current_day > total_days:
            plan_status = "past_last_day"
        else:
            plan_status = "in_progress"

        todays_items = [
            item
            for item in items
            if item.day_number == current_day
        ]

        overdue_items = [
            item
            for item in items
            if item.day_number < current_day
            and item.status in ("pending", "skipped")
        ]

        completed_today = [
            item
            for item in todays_items
            if item.status == "completed"
        ]

        return jsonify({
            "status": "success",
            "goal_id": goal.id,
            "roadmap_id": roadmap.id,
            "roadmap_version": roadmap.version_number,
            "date": today.isoformat(),
            "start_date": start_date.isoformat(),
            "current_day": current_day,
            "total_days": total_days,
            "plan_status": plan_status,
            "summary": {
                "tasks_total": len(todays_items),
                "tasks_completed": len(completed_today),
                "planned_minutes_today": sum(
                    item.planned_minutes
                    for item in todays_items
                ),
                "completed_minutes_today": sum(
                    item.planned_minutes
                    for item in completed_today
                ),
                "overdue_count": len(overdue_items),
                "overdue_minutes": sum(
                    item.planned_minutes
                    for item in overdue_items
                )
            },
            "tasks": [
                _item_to_dict(
                    item,
                    topic_names,
                    start_date
                )
                for item in todays_items
            ],
            "overdue_tasks": [
                _item_to_dict(
                    item,
                    topic_names,
                    start_date
                )
                for item in overdue_items
            ]
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Could not load today's tasks.",
            "error": str(error)
        }), 500


def _update_task(item_id, new_status):
    item = db.session.get(
        RoadmapItem,
        item_id
    )

    if item is None:
        return jsonify({
            "status": "error",
            "message": "Task not found."
        }), 404

    roadmap = db.session.get(
        Roadmap,
        item.roadmap_id
    )

    if roadmap is None or roadmap.status != "active":
        return jsonify({
            "status": "error",
            "message": (
                "This task belongs to an older roadmap version. "
                "Only tasks from the active roadmap can be changed."
            )
        }), 409

    goal = db.session.get(Goal, roadmap.goal_id)
    if goal is None:
        return jsonify({
            "status": "error",
            "message": "Associated goal not found."
        }), 404

    allowed, msg = check_goal_access(goal)
    if not allowed:
        code = 401 if ("Authentication required" in msg or "token" in msg.lower()) else 403
        return jsonify({
            "status": "error",
            "message": msg
        }), code

    data = request.get_json(silent=True) or {}

    actual_minutes = item.planned_minutes

    if new_status == "skipped":
        actual_minutes = 0

    elif "actual_minutes" in data:
        try:
            actual_minutes = int(data["actual_minutes"])
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "actual_minutes must be a whole number."
            }), 400

        if actual_minutes < 0:
            return jsonify({
                "status": "error",
                "message": "actual_minutes cannot be negative."
            }), 400

    try:
        start_date = _roadmap_start_date(roadmap)

        study_date = start_date + timedelta(
            days=item.day_number - 1
        )

        log = StudyLog.query.filter_by(
            goal_id=roadmap.goal_id,
            topic_id=item.topic_id,
            study_date=study_date
        ).first()

        if log is None:
            log = StudyLog(
                goal_id=roadmap.goal_id,
                topic_id=item.topic_id,
                study_date=study_date,
                planned_minutes=item.planned_minutes,
                actual_minutes=0,
                status="pending"
            )

            db.session.add(log)

        item.status = new_status

        log.planned_minutes = item.planned_minutes
        log.actual_minutes = actual_minutes
        log.status = new_status
        log.completed_at = (
            datetime.utcnow()
            if new_status == "completed"
            else None
        )

        db.session.commit()

        topic = db.session.get(
            Topic,
            item.topic_id
        )

        topic_names = {
            item.topic_id: topic.name if topic else "Unknown topic"
        }

        return jsonify({
            "status": "success",
            "message": (
                "Task marked as completed."
                if new_status == "completed"
                else "Task skipped."
            ),
            "task": _item_to_dict(
                item,
                topic_names,
                start_date
            ),
            "study_log": {
                "id": log.id,
                "study_date": log.study_date.isoformat(),
                "planned_minutes": log.planned_minutes,
                "actual_minutes": log.actual_minutes,
                "status": log.status
            }
        }), 200

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Could not update the task.",
            "error": str(error)
        }), 500


@tasks_bp.post("/<int:item_id>/complete")
def complete_task(item_id):
    return _update_task(item_id, "completed")


@tasks_bp.post("/<int:item_id>/skip")
def skip_task(item_id):
    return _update_task(item_id, "skipped")