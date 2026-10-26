from datetime import datetime
from flask import Blueprint, jsonify, request, g

from extensions import db
from models import Goal, WeeklyReflection
from middleware.auth import check_goal_access

reflections_bp = Blueprint(
    "reflections",
    __name__,
    url_prefix="/api/v1/reflections"
)


@reflections_bp.post("")
@reflections_bp.post("/")
def create_reflection():
    data = request.get_json(silent=True) or {}
    goal_id = data.get("goal_id")

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id is required."
        }), 400

    try:
        goal_id = int(goal_id)
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "goal_id must be a number."
        }), 400

    goal = db.session.get(Goal, goal_id)
    if not goal:
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

    confidence_level = data.get("confidence_level")
    difficulty_rating = data.get("difficulty_rating")

    if confidence_level is None or difficulty_rating is None:
        return jsonify({
            "status": "error",
            "message": "confidence_level and difficulty_rating are required."
        }), 400

    try:
        confidence_level = int(confidence_level)
        difficulty_rating = int(difficulty_rating)
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "confidence_level and difficulty_rating must be whole numbers."
        }), 400

    if not (1 <= confidence_level <= 5):
        return jsonify({
            "status": "error",
            "message": "confidence_level must be between 1 and 5."
        }), 400

    if not (1 <= difficulty_rating <= 5):
        return jsonify({
            "status": "error",
            "message": "difficulty_rating must be between 1 and 5."
        }), 400

    study_day = data.get("study_day", 7)
    try:
        study_day = int(study_day)
    except (TypeError, ValueError):
        study_day = 7

    week_number = data.get("week_number")
    if week_number is not None:
        try:
            week_number = int(week_number)
        except (TypeError, ValueError):
            week_number = max(1, (study_day + 6) // 7)
    else:
        week_number = max(1, (study_day + 6) // 7)

    notes = data.get("notes", "")
    if isinstance(notes, str):
        notes = notes.strip() or None
    else:
        notes = None

    user_id = g.user_id if hasattr(g, "user_id") and g.user_id else goal.user_id

    try:
        reflection = WeeklyReflection(
            goal_id=goal.id,
            user_id=user_id,
            week_number=week_number,
            study_day=study_day,
            confidence_level=confidence_level,
            difficulty_rating=difficulty_rating,
            notes=notes,
            created_at=datetime.utcnow()
        )
        db.session.add(reflection)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Weekly reflection saved successfully.",
            "reflection": reflection.to_dict()
        }), 201

    except Exception as err:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Could not save weekly reflection.",
            "error": str(err)
        }), 500


@reflections_bp.get("")
@reflections_bp.get("/")
def list_reflections():
    goal_id = request.args.get("goal_id", type=int)

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id query parameter is required."
        }), 400

    goal = db.session.get(Goal, goal_id)
    if not goal:
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

    reflections = WeeklyReflection.query.filter_by(
        goal_id=goal.id
    ).order_by(
        WeeklyReflection.week_number.desc(),
        WeeklyReflection.id.desc()
    ).all()

    return jsonify({
        "status": "success",
        "count": len(reflections),
        "reflections": [r.to_dict() for r in reflections]
    }), 200


@reflections_bp.get("/status")
def reflection_status():
    goal_id = request.args.get("goal_id", type=int)

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id query parameter is required."
        }), 400

    goal = db.session.get(Goal, goal_id)
    if not goal:
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

    day = request.args.get("day", type=int, default=7)
    week_number = max(1, (day + 6) // 7) if day > 0 else 1
    is_due = (day > 0 and day % 7 == 0)

    existing = WeeklyReflection.query.filter_by(
        goal_id=goal.id,
        week_number=week_number
    ).first()

    submitted = (existing is not None)

    return jsonify({
        "status": "success",
        "goal_id": goal.id,
        "current_day": day,
        "week_number": week_number,
        "is_due": is_due,
        "submitted": submitted,
        "should_prompt": is_due and not submitted,
        "reflection": existing.to_dict() if existing else None
    }), 200

