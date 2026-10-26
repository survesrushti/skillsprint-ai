from datetime import datetime
from flask import Blueprint, jsonify, request, g

from extensions import db
from models import Goal
from middleware.auth import check_goal_access


goals_bp = Blueprint(
    "goals",
    __name__,
    url_prefix="/api/v1/goals"
)


@goals_bp.post("")
def create_goal():
    current_uid = getattr(g, "user_id", None)
    if current_uid is None:
        return jsonify({
            "status": "error",
            "message": "Authentication required to create a goal."
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body is required."
        }), 400

    required_fields = [
        "track_id",
        "skill_level",
        "study_hours_per_day",
        "target_date"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "status": "error",
            "message": "Missing required fields.",
            "missing_fields": missing_fields
        }), 400

    try:
        target_date = datetime.strptime(
            data["target_date"],
            "%d/%m/%Y"
        ).date()

        raw_known = data.get("known_topics", [])
        if isinstance(raw_known, list):
            known_topics_str = ",".join(
                str(item).strip()
                for item in raw_known
                if str(item).strip()
            )
        elif isinstance(raw_known, str):
            known_topics_str = raw_known.strip()
        else:
            known_topics_str = ""

        # Strictly bind goal to the authenticated user; ignore any spoofed user_id in payload
        user_id = current_uid
        track_id = int(data["track_id"])

        # Enforce V1 single active goal constraint:
        # Mark prior active goals for this specific authenticated user as superseded.
        Goal.query.filter(
            Goal.status == "active",
            Goal.user_id == user_id
        ).update(
            {"status": "superseded"},
            synchronize_session=False
        )

        goal = Goal(
            user_id=user_id,
            track_id=track_id,
            skill_level=data["skill_level"],
            study_hours_per_day=float(
                data["study_hours_per_day"]
            ),
            target_date=target_date,
            known_topics=known_topics_str,
            commitment=bool(
                data.get("commitment", False)
            ),
            status="active"
        )

        db.session.add(goal)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Goal created successfully.",
            "goal": {
                "id": goal.id,
                "user_id": goal.user_id,
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime(
                    "%d/%m/%Y"
                ),
                "known_topics": (
                    [t.strip() for t in goal.known_topics.split(",") if t.strip()]
                    if goal.known_topics
                    else []
                ),
                "commitment": goal.commitment,
                "status": goal.status
            }
        }), 201

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid date or numeric value."
        }), 400

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Could not create goal.",
            "error": str(error)
        }), 500


@goals_bp.get("/active")
def get_active_goal():
    current_uid = getattr(g, "user_id", None)
    if current_uid is None:
        return jsonify({
            "status": "error",
            "message": "Authentication required to access active goal."
        }), 401

    track_id = request.args.get("track_id", type=int)

    try:
        # Strictly scoped to the authenticated user; ignores client user_id param
        query = Goal.query.filter(
            Goal.status == "active",
            Goal.user_id == current_uid
        )

        if track_id is not None:
            query = query.filter(Goal.track_id == track_id)

        goal = query.order_by(Goal.id.desc()).first()

        if goal is None:
            return jsonify({
                "status": "error",
                "message": "No active goal found."
            }), 404

        return jsonify({
            "status": "success",
            "goal": {
                "id": goal.id,
                "user_id": goal.user_id,
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime("%d/%m/%Y"),
                "known_topics": (
                    [t.strip() for t in goal.known_topics.split(",") if t.strip()]
                    if goal.known_topics
                    else []
                ),
                "commitment": goal.commitment,
                "status": goal.status
            }
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Could not retrieve active goal.",
            "error": str(error)
        }), 500


@goals_bp.get("/<int:goal_id>")
def get_goal(goal_id):
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

        return jsonify({
            "status": "success",
            "goal": {
                "id": goal.id,
                "user_id": goal.user_id,
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime("%d/%m/%Y"),
                "known_topics": (
                    [t.strip() for t in goal.known_topics.split(",") if t.strip()]
                    if goal.known_topics
                    else []
                ),
                "commitment": goal.commitment,
                "status": goal.status
            }
        }), 200

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": "Could not retrieve goal.",
            "error": str(error)
        }), 500
