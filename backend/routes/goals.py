from datetime import datetime

from flask import Blueprint, jsonify, request

from extensions import db
from models import Goal


goals_bp = Blueprint(
    "goals",
    __name__,
    url_prefix="/api/v1/goals"
)


@goals_bp.post("")
def create_goal():
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

        goal = Goal(
            track_id=int(data["track_id"]),
            skill_level=data["skill_level"],
            study_hours_per_day=float(
                data["study_hours_per_day"]
            ),
            target_date=target_date,
            known_topics=",".join(
                data.get("known_topics", [])
            ),
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
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime(
                    "%d/%m/%Y"
                ),
                "known_topics": data.get(
                    "known_topics",
                    []
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