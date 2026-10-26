import os
import sys
from datetime import date, timedelta

# Ensure backend directory is in sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import create_app
from extensions import db
from models import Goal, Track
from tests.jwt_test_helpers import get_auth_headers


def test_create_goal_sets_status_active():
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        headers = get_auth_headers("active_goal_user_1")

        with app.test_client() as client:
            res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "intermediate",
                    "study_hours_per_day": 1.5,
                    "target_date": target,
                    "commitment": True,
                },
            )

            assert res.status_code == 201
            data = res.get_json()
            assert data["status"] == "success"
            assert data["goal"]["status"] == "active"
            assert data["goal"]["skill_level"] == "intermediate"


def test_single_active_goal_enforcement():
    """
    Core V1 constraint: Creating a new goal for a user/track must supersede
    any previously active goal.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=45)).strftime("%d/%m/%Y")
        headers = get_auth_headers("active_goal_user_2")

        with app.test_client() as client:
            # Step 1: Create First Goal
            res1 = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 1.0,
                    "target_date": target,
                    "known_topics": ["HTML Fundamentals"],
                    "commitment": True,
                },
            )
            assert res1.status_code == 201
            goal1_id = res1.get_json()["goal"]["id"]

            goal1_db = db.session.get(Goal, goal1_id)
            assert goal1_db.status == "active"

            # Step 2: Create Second Goal for the same user
            res2 = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "advanced",
                    "study_hours_per_day": 2.5,
                    "target_date": target,
                    "known_topics": ["CSS Fundamentals"],
                    "commitment": True,
                },
            )
            assert res2.status_code == 201
            goal2_id = res2.get_json()["goal"]["id"]

            # Step 3: Verify Goal 1 was superseded and Goal 2 is active
            db.session.expire_all()
            goal1_refreshed = db.session.get(Goal, goal1_id)
            goal2_refreshed = db.session.get(Goal, goal2_id)

            assert goal1_refreshed.status == "superseded"
            assert goal2_refreshed.status == "active"


def test_get_active_goal():
    """
    Verify GET /api/v1/goals/active returns the latest active goal.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=60)).strftime("%d/%m/%Y")
        headers = get_auth_headers("active_goal_user_3")

        with app.test_client() as client:
            # Create a goal
            post_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "known_topics": ["HTML Fundamentals", "CSS Fundamentals"],
                    "commitment": True,
                },
            )
            assert post_res.status_code == 201
            created_goal_id = post_res.get_json()["goal"]["id"]

            # Retrieve active goal for this authenticated user
            get_res = client.get("/api/v1/goals/active", headers=headers)
            assert get_res.status_code == 200
            data = get_res.get_json()

            assert data["status"] == "success"
            assert data["goal"]["id"] == created_goal_id
            assert data["goal"]["status"] == "active"
            assert data["goal"]["known_topics"] == ["HTML Fundamentals", "CSS Fundamentals"]


def test_get_active_goal_filtering_and_404():
    """
    Verify filtering by track_id and proper 404 when no active goal exists.
    """
    app = create_app()
    headers = get_auth_headers("active_goal_user_4_empty")

    with app.test_client() as client:
        # User has no active goal
        res = client.get("/api/v1/goals/active", headers=headers)
        assert res.status_code == 404
        assert res.get_json()["status"] == "error"
        assert res.get_json()["message"] == "No active goal found."

        # Nonexistent track filter
        res_track = client.get("/api/v1/goals/active?track_id=999999", headers=headers)
        assert res_track.status_code == 404


def test_get_goal_by_id():
    """
    Verify GET /api/v1/goals/<id> returns the goal or 404.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        headers = get_auth_headers("active_goal_user_5")

        with app.test_client() as client:
            post_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                },
            )
            goal_id = post_res.get_json()["goal"]["id"]

            # Existing goal owned by user
            get_res = client.get(f"/api/v1/goals/{goal_id}", headers=headers)
            assert get_res.status_code == 200
            assert get_res.get_json()["goal"]["id"] == goal_id

            # Nonexistent goal
            bad_res = client.get("/api/v1/goals/999999", headers=headers)
            assert bad_res.status_code == 404
