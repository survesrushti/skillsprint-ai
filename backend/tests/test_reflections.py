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
from models import Goal, Track, WeeklyReflection, User
from tests.jwt_test_helpers import get_auth_headers


def test_create_reflection_validation():
    """Verify validation rules on POST /api/v1/reflections."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_reflection_val_user")

        with app.test_client() as client:
            # 1. Setup goal
            goal_res = client.post(
                "/api/v1/goals",
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                },
                headers=user_headers,
            )
            assert goal_res.status_code == 201
            goal_id = goal_res.get_json()["goal"]["id"]

            # 2. Missing goal_id returns 400
            res = client.post(
                "/api/v1/reflections",
                json={"confidence_level": 4, "difficulty_rating": 3},
                headers=user_headers,
            )
            assert res.status_code == 400

            # 3. Missing confidence_level returns 400
            res = client.post(
                "/api/v1/reflections",
                json={"goal_id": goal_id, "difficulty_rating": 3},
                headers=user_headers,
            )
            assert res.status_code == 400

            # 4. Out of bounds confidence_level returns 400
            res = client.post(
                "/api/v1/reflections",
                json={"goal_id": goal_id, "confidence_level": 6, "difficulty_rating": 3},
                headers=user_headers,
            )
            assert res.status_code == 400

            res = client.post(
                "/api/v1/reflections",
                json={"goal_id": goal_id, "confidence_level": 0, "difficulty_rating": 3},
                headers=user_headers,
            )
            assert res.status_code == 400

            # 5. Out of bounds difficulty_rating returns 400
            res = client.post(
                "/api/v1/reflections",
                json={"goal_id": goal_id, "confidence_level": 4, "difficulty_rating": 10},
                headers=user_headers,
            )
            assert res.status_code == 400

            # 6. Non-existent goal_id returns 404
            res = client.post(
                "/api/v1/reflections",
                json={"goal_id": 999999, "confidence_level": 4, "difficulty_rating": 3},
                headers=user_headers,
            )
            assert res.status_code == 404


def test_create_and_list_reflections_success():
    """Verify creating a weekly reflection and listing all reflections for a goal."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=40)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_reflection_success_user")

        with app.test_client() as client:
            # 1. Setup goal
            goal_res = client.post(
                "/api/v1/goals",
                json={
                    "track_id": track.id,
                    "skill_level": "intermediate",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                },
                headers=user_headers,
            )
            goal_id = goal_res.get_json()["goal"]["id"]

            # 2. Submit reflection for Week 1 (Day 7)
            notes_text = "Mastered CSS grid and flexbox. Feeling steady."
            post_res = client.post(
                "/api/v1/reflections",
                json={
                    "goal_id": goal_id,
                    "week_number": 1,
                    "study_day": 7,
                    "confidence_level": 4,
                    "difficulty_rating": 3,
                    "notes": notes_text,
                },
                headers=user_headers,
            )
            assert post_res.status_code == 201
            post_data = post_res.get_json()
            assert post_data["status"] == "success"
            reflection = post_data["reflection"]
            assert reflection["goal_id"] == goal_id
            assert reflection["week_number"] == 1
            assert reflection["study_day"] == 7
            assert reflection["confidence_level"] == 4
            assert reflection["difficulty_rating"] == 3
            assert reflection["notes"] == notes_text
            assert "created_at" in reflection

            # 3. List reflections for this goal
            list_res = client.get(
                f"/api/v1/reflections?goal_id={goal_id}",
                headers=user_headers,
            )
            assert list_res.status_code == 200
            list_data = list_res.get_json()
            assert list_data["status"] == "success"
            assert list_data["count"] >= 1
            assert any(r["id"] == reflection["id"] for r in list_data["reflections"])


def test_reflection_status_and_weekly_due_logic():
    """Verify reflection due status on every 7th day of study."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=35)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_reflection_status_user")

        with app.test_client() as client:
            goal_res = client.post(
                "/api/v1/goals",
                json={
                    "track_id": track.id,
                    "skill_level": "intermediate",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                },
                headers=user_headers,
            )
            goal_id = goal_res.get_json()["goal"]["id"]

            # Day 3: Not due
            res_day3 = client.get(
                f"/api/v1/reflections/status?goal_id={goal_id}&day=3",
                headers=user_headers,
            )
            assert res_day3.status_code == 200
            data_day3 = res_day3.get_json()
            assert data_day3["is_due"] is False
            assert data_day3["should_prompt"] is False

            # Day 7: Due, not yet submitted -> should prompt!
            res_day7 = client.get(
                f"/api/v1/reflections/status?goal_id={goal_id}&day=7",
                headers=user_headers,
            )
            assert res_day7.status_code == 200
            data_day7 = res_day7.get_json()
            assert data_day7["is_due"] is True
            assert data_day7["submitted"] is False
            assert data_day7["should_prompt"] is True

            # Submit reflection for Day 7 (Week 1)
            client.post(
                "/api/v1/reflections",
                json={
                    "goal_id": goal_id,
                    "study_day": 7,
                    "confidence_level": 5,
                    "difficulty_rating": 2,
                    "notes": "Everything is on track.",
                },
                headers=user_headers,
            )

            # Check Day 7 status again: Now submitted -> should_prompt is False
            res_day7_after = client.get(
                f"/api/v1/reflections/status?goal_id={goal_id}&day=7",
                headers=user_headers,
            )
            assert res_day7_after.status_code == 200
            data_day7_after = res_day7_after.get_json()
            assert data_day7_after["is_due"] is True
            assert data_day7_after["submitted"] is True
            assert data_day7_after["should_prompt"] is False

            # Check Day 14 (Week 2): Due again for the next cycle
            res_day14 = client.get(
                f"/api/v1/reflections/status?goal_id={goal_id}&day=14",
                headers=user_headers,
            )
            assert res_day14.status_code == 200
            data_day14 = res_day14.get_json()
            assert data_day14["is_due"] is True
            assert data_day14["submitted"] is False
            assert data_day14["should_prompt"] is True


def test_reflection_user_isolation():
    """Verify User B cannot access or record reflections for User A's goal."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")

        headers_a = get_auth_headers("reflection_user_alice")
        headers_b = get_auth_headers("reflection_user_bob")

        with app.test_client() as client:
            goal_res = client.post(
                "/api/v1/goals",
                json={
                    "track_id": track.id,
                    "skill_level": "intermediate",
                    "study_hours_per_day": 1.5,
                    "target_date": target,
                    "commitment": True,
                },
                headers=headers_a,
            )
            goal_id = goal_res.get_json()["goal"]["id"]

            # User B attempts to submit reflection for User A's goal -> 403 Forbidden
            post_res = client.post(
                "/api/v1/reflections",
                json={
                    "goal_id": goal_id,
                    "study_day": 7,
                    "confidence_level": 3,
                    "difficulty_rating": 3,
                },
                headers=headers_b,
            )
            assert post_res.status_code == 403

            # User B attempts to list User A's reflections -> 403 Forbidden
            list_res = client.get(
                f"/api/v1/reflections?goal_id={goal_id}",
                headers=headers_b,
            )
            assert list_res.status_code == 403

