
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from extensions import db
from models import Goal, Roadmap, RoadmapItem, StudyLog
from middleware.auth import check_goal_access


progress_bp = Blueprint(
    "progress",
    __name__,
    url_prefix="/api/v1/progress"
)


def _roadmap_start_date(roadmap):
    created = roadmap.created_at or datetime.utcnow()

    return created.replace(
        tzinfo=timezone.utc
    ).astimezone().date()


def _active_roadmap(goal_id):
    return Roadmap.query.filter_by(
        goal_id=goal_id,
        status="active"
    ).order_by(
        Roadmap.version_number.desc()
    ).first()


@progress_bp.get("/summary")
def get_progress_summary():
    goal_id = request.args.get("goal_id", type=int)

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id is required."
        }), 400

    date_text = request.args.get("date")

    try:
        report_date = (
            datetime.strptime(date_text, "%Y-%m-%d").date()
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

        total_tasks = len(items)
        completed_tasks = sum(
            item.status == "completed" for item in items
        )

        total_planned_minutes = sum(
            item.planned_minutes for item in items
        )

        total_days = max(
            (item.day_number for item in items),
            default=0
        )

        current_day = (report_date - start_date).days + 1

        elapsed_items = [
            item for item in items
            if item.day_number <= current_day
        ]

        expected_tasks = len(elapsed_items)

        completed_by_date = sum(
            item.status == "completed"
            for item in elapsed_items
        )

        completion_percentage = (
            round(completed_tasks / total_tasks * 100, 2)
            if total_tasks else 0
        )

        expected_percentage = (
            round(expected_tasks / total_tasks * 100, 2)
            if total_tasks else 0
        )

        actual_percentage = (
            round(completed_by_date / total_tasks * 100, 2)
            if total_tasks else 0
        )

        logs = StudyLog.query.filter(
            StudyLog.goal_id == goal_id,
            StudyLog.study_date >= start_date,
            StudyLog.study_date <= report_date,
            StudyLog.status == "completed"
        ).all()

        actual_minutes = sum(
            log.actual_minutes for log in logs
        )

        completed_dates = {
            log.study_date for log in logs
        }

        streak_end = report_date

        if streak_end not in completed_dates:
            streak_end = report_date - timedelta(days=1)

        current_streak = 0

        if streak_end in completed_dates:
            streak_date = streak_end

            while streak_date in completed_dates:
                current_streak += 1
                streak_date -= timedelta(days=1)

        return jsonify({
            "status": "success",
            "goal_id": goal.id,
            "roadmap_id": roadmap.id,
            "roadmap_version": roadmap.version_number,
            "report_date": report_date.isoformat(),
            "start_date": start_date.isoformat(),
            "current_day": current_day,
            "total_days": total_days,
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "remaining_tasks": total_tasks - completed_tasks,
                "completion_percentage": completion_percentage,
                "total_planned_minutes": total_planned_minutes,
                "actual_study_minutes": actual_minutes
            },
            "progress": {
                "expected_tasks_by_date": expected_tasks,
                "completed_tasks_by_date": completed_by_date,
                "expected_percentage": expected_percentage,
                "actual_percentage": actual_percentage,
                "progress_difference": round(
                    actual_percentage - expected_percentage,
                    2
                )
            },
            "streak": {
                "current_streak_days": current_streak,
                "completed_study_dates": len(completed_dates)
            }
        }), 200

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Could not calculate progress summary.",
            "error": str(error)
        }), 500