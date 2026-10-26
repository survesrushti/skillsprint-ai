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
from models import Goal, Track, Topic, Roadmap, RoadmapItem
from tests.jwt_test_helpers import get_auth_headers


def test_health_route():
    """Verify GET /api/v1/health returns HTTP 200 with service health status."""
    app = create_app()

    with app.test_client() as client:
        res = client.get("/api/v1/health")
        assert res.status_code == 200

        data = res.get_json()
        assert data.get("status") in ("ok", "healthy")
        assert "message" in data


def test_goals_crud_and_validation_routes():
    """Verify POST /api/v1/goals, GET /api/v1/goals/<id>, and GET /api/v1/goals/active."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        assert track is not None

        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_routes_user_goal")

        with app.test_client() as client:
            # 1. Validation error on missing required fields
            bad_res = client.post(
                "/api/v1/goals",
                json={"track_id": track.id},
                headers=user_headers,
            )
            assert bad_res.status_code == 400

            # 2. Successfully create active goal
            create_res = client.post(
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
            assert create_res.status_code == 201
            create_data = create_res.get_json()
            assert create_data["status"] == "success"
            goal_id = create_data["goal"]["id"]
            assert create_data["goal"]["status"] == "active"

            # 3. Fetch goal by ID
            get_res = client.get(f"/api/v1/goals/{goal_id}", headers=user_headers)
            assert get_res.status_code == 200
            get_data = get_res.get_json()
            assert get_data["goal"]["id"] == goal_id
            assert get_data["goal"]["skill_level"] == "intermediate"

            # 4. Fetch non-existent goal returns 404
            not_found_res = client.get("/api/v1/goals/999999", headers=user_headers)
            assert not_found_res.status_code == 404

            # 5. Fetch active goal
            active_res = client.get("/api/v1/goals/active", headers=user_headers)
            assert active_res.status_code == 200
            active_data = active_res.get_json()
            assert active_data["status"] == "success"
            assert active_data["goal"]["id"] == goal_id


def test_roadmap_generate_and_active_routes():
    """Verify POST /api/v1/roadmap/generate and GET /api/v1/roadmap/active."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=45)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_routes_user_roadmap")

        with app.test_client() as client:
            # 1. Validation error when goal_id is missing
            bad_gen = client.post(
                "/api/v1/roadmap/generate",
                json={},
                headers=user_headers,
            )
            assert bad_gen.status_code == 400

            # 2. Setup goal
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

            # 3. Generate roadmap
            gen_res = client.post(
                "/api/v1/roadmap/generate",
                json={"goal_id": goal_id},
                headers=user_headers,
            )
            assert gen_res.status_code == 200
            gen_data = gen_res.get_json()
            assert gen_data["status"] == "success"
            assert "roadmap_id" in gen_data
            assert gen_data["roadmap_version"] == 1
            assert isinstance(gen_data["roadmap"], list)
            assert len(gen_data["roadmap"]) > 0

            # 4. Fetch active roadmap
            active_rm_res = client.get(
                f"/api/v1/roadmap/active?goal_id={goal_id}",
                headers=user_headers,
            )
            assert active_rm_res.status_code == 200
            active_rm_data = active_rm_res.get_json()
            assert active_rm_data["status"] == "success"
            assert active_rm_data["roadmap_version"] == 1
            assert isinstance(active_rm_data["roadmap"], list)
            assert len(active_rm_data["roadmap"]) > 0
            assert active_rm_data["items_saved"] > 0

            # 5. Missing goal_id query parameter returns 400
            bad_active_rm = client.get("/api/v1/roadmap/active", headers=user_headers)
            assert bad_active_rm.status_code == 400


def test_tasks_today_and_task_action_routes():
    """Verify GET /api/v1/tasks/today, POST /api/v1/tasks/<id>/complete, and POST /api/v1/tasks/<id>/skip."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_routes_user_tasks")

        with app.test_client() as client:
            # Setup goal and roadmap
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

            gen_res = client.post(
                "/api/v1/roadmap/generate",
                json={"goal_id": goal_id},
                headers=user_headers,
            )
            assert gen_res.status_code == 200
            gen_data = gen_res.get_json()
            roadmap_id = gen_data["roadmap_id"]

            # 1. Fetch today's tasks
            today_res = client.get(
                f"/api/v1/tasks/today?goal_id={goal_id}",
                headers=user_headers,
            )
            assert today_res.status_code == 200
            today_data = today_res.get_json()
            assert today_data["status"] == "success"
            assert "summary" in today_data
            assert "tasks" in today_data
            assert today_data["summary"]["tasks_total"] > 0

            # Find items belonging to this roadmap
            items = RoadmapItem.query.filter_by(roadmap_id=roadmap_id).order_by(RoadmapItem.id).all()
            assert len(items) >= 2

            first_item = items[0]
            second_item = items[1]

            # 2. Complete first task
            complete_res = client.post(
                f"/api/v1/tasks/{first_item.id}/complete",
                json={"actual_minutes": first_item.planned_minutes},
                headers=user_headers,
            )
            assert complete_res.status_code == 200
            complete_data = complete_res.get_json()
            assert complete_data["status"] == "success"
            assert complete_data["task"]["status"] == "completed"
            assert complete_data["study_log"]["status"] == "completed"

            # 3. Skip second task
            skip_res = client.post(
                f"/api/v1/tasks/{second_item.id}/skip",
                headers=user_headers,
            )
            assert skip_res.status_code == 200
            skip_data = skip_res.get_json()
            assert skip_data["status"] == "success"
            assert skip_data["task"]["status"] == "skipped"

            # 4. Action on non-existent task returns 404
            not_found_task = client.post(
                "/api/v1/tasks/999999/complete",
                headers=user_headers,
            )
            assert not_found_task.status_code == 404


def test_roadmap_reschedule_route():
    """Verify POST /api/v1/roadmap/reschedule integration with CI engines."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=20)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_routes_user_reschedule")

        with app.test_client() as client:
            # 1. Missing goal_id returns 400
            bad_res = client.post(
                "/api/v1/roadmap/reschedule",
                json={},
                headers=user_headers,
            )
            assert bad_res.status_code == 400

            # 2. Setup goal and generate initial roadmap (v1)
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

            client.post(
                "/api/v1/roadmap/generate",
                json={"goal_id": goal_id},
                headers=user_headers,
            )

            # 3. Call reschedule endpoint without backlog items (keeps current roadmap)
            resched_res_clean = client.post(
                "/api/v1/roadmap/reschedule",
                json={"goal_id": goal_id},
                headers=user_headers,
            )
            assert resched_res_clean.status_code == 200
            resched_clean_data = resched_res_clean.get_json()
            assert resched_clean_data["status"] == "success"
            assert resched_clean_data["replanned"] is False
            assert "No skipped or overdue tasks" in resched_clean_data["message"]

            # 4. Call reschedule endpoint with force=True to trigger full CI replanning pipeline
            resched_res = client.post(
                "/api/v1/roadmap/reschedule",
                json={"goal_id": goal_id, "force": True},
                headers=user_headers,
            )
            assert resched_res.status_code == 200
            resched_data = resched_res.get_json()
            assert resched_data["status"] == "success"
            assert resched_data["replanned"] is True
            assert "ci" in resched_data
            assert "fuzzy" in resched_data["ci"]
            assert "expert" in resched_data["ci"]
            assert "roadmap" in resched_data
            assert isinstance(resched_data["roadmap"], list)
            assert resched_data["roadmap_version"] >= 2
            assert resched_data["saved"] is True


def test_progress_summary_route():
    """Verify GET /api/v1/progress/summary calculates learning progress metrics."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_routes_user_progress")

        with app.test_client() as client:
            # 1. Missing goal_id returns 400
            bad_req = client.get("/api/v1/progress/summary", headers=user_headers)
            assert bad_req.status_code == 400

            # 2. Setup goal and roadmap
            goal_res = client.post(
                "/api/v1/goals",
                json={
                    "track_id": track.id,
                    "skill_level": "intermediate",
                    "study_hours_per_day": 1.5,
                    "target_date": target,
                    "commitment": True,
                },
                headers=user_headers,
            )
            goal_id = goal_res.get_json()["goal"]["id"]

            client.post(
                "/api/v1/roadmap/generate",
                json={"goal_id": goal_id},
                headers=user_headers,
            )

            # 3. Fetch progress summary
            prog_res = client.get(
                f"/api/v1/progress/summary?goal_id={goal_id}",
                headers=user_headers,
            )
            assert prog_res.status_code == 200
            prog_data = prog_res.get_json()
            assert prog_data["status"] == "success"
            assert "summary" in prog_data
            assert "progress" in prog_data
            assert "streak" in prog_data
            assert prog_data["summary"]["total_tasks"] > 0
            assert "completion_percentage" in prog_data["summary"]
            assert "actual_percentage" in prog_data["progress"]
            assert "expected_percentage" in prog_data["progress"]


def test_tracks_and_topic_resources_routes():
    """Verify GET /api/v1/tracks, /api/v1/tracks/<slug>, and /api/v1/topics/<id>/resources."""
    app = create_app()

    with app.app_context():
        first_topic = Topic.query.first()
        assert first_topic is not None

        with app.test_client() as client:
            # 1. List tracks
            tracks_res = client.get("/api/v1/tracks")
            assert tracks_res.status_code == 200
            tracks_data = tracks_res.get_json()
            assert tracks_data["status"] == "success"
            assert tracks_data["count"] >= 3

            # 2. Get specific track
            track_res = client.get("/api/v1/tracks/full-stack-development")
            assert track_res.status_code == 200
            track_data = track_res.get_json()
            assert track_data["track"]["slug"] == "full-stack-development"

            # 3. Get topic resources
            res_res = client.get(f"/api/v1/topics/{first_topic.id}/resources")
            assert res_res.status_code == 200
            res_data = res_res.get_json()
            assert res_data["status"] == "success"
            assert res_data["topic_id"] == first_topic.id
            assert isinstance(res_data["resources"], list)


def test_weekly_reflections_routes():
    """Verify POST /api/v1/reflections, GET /api/v1/reflections, and GET /api/v1/reflections/status."""
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        user_headers = get_auth_headers("test_routes_user_reflections")

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

            # 1. Check status on Day 7 (due, not submitted)
            status_res = client.get(
                f"/api/v1/reflections/status?goal_id={goal_id}&day=7",
                headers=user_headers,
            )
            assert status_res.status_code == 200
            status_data = status_res.get_json()
            assert status_data["is_due"] is True
            assert status_data["should_prompt"] is True

            # 2. Submit reflection
            submit_res = client.post(
                "/api/v1/reflections",
                json={
                    "goal_id": goal_id,
                    "week_number": 1,
                    "study_day": 7,
                    "confidence_level": 4,
                    "difficulty_rating": 3,
                    "notes": "Good progress on weekly milestones.",
                },
                headers=user_headers,
            )
            assert submit_res.status_code == 201
            submit_data = submit_res.get_json()
            assert submit_data["status"] == "success"
            assert submit_data["reflection"]["confidence_level"] == 4

            # 3. List reflections
            list_res = client.get(
                f"/api/v1/reflections?goal_id={goal_id}",
                headers=user_headers,
            )
            assert list_res.status_code == 200
            list_data = list_res.get_json()
            assert list_data["count"] >= 1

