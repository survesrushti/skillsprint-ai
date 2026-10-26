import os
import sys
import base64
import json
from datetime import date, timedelta

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import create_app
from extensions import db
from models import User, Goal, Track, Topic, Roadmap, RoadmapItem, WeeklyReflection


from tests.jwt_test_helpers import make_test_jwt

def _make_mock_clerk_jwt(sub: str, email: str = "learner@example.com", name: str = "Learner Journey Tester") -> str:
    return make_test_jwt(sub=sub, email=email, name=name)


def test_complete_learner_journey_end_to_end():
    """
    Comprehensive End-to-End Test for the full Learner Journey:
    1. Sign-in simulation with Clerk JWT
    2. Track selection & track details lookup
    3. Goal creation with known-topic exclusions
    4. Roadmap generation ensuring known topics are excluded
    5. Active roadmap load & verification
    6. Day 1 task retrieval
    7. Daily task completion & actual minutes logging
    8. Alternative resource swapping
    9. Progress tracking & completion percentage verification
    10. Task skipping & missed work simulation
    11. Adaptive rescheduling with simulated date override
    12. Day 7 weekly reflection prompt verification & reflection submission
    """
    app = create_app()

    clerk_id = "user_e2e_learner_42"
    learner_token = _make_mock_clerk_jwt(sub=clerk_id, email="alex.learner@skillsprint.ai", name="Alex Learner")
    auth_headers = {"Authorization": f"Bearer {learner_token}"}

    with app.test_client() as client:
        # Step 1: Browse tracks (catalog)
        res_tracks = client.get("/api/v1/tracks")
        assert res_tracks.status_code == 200
        tracks_data = res_tracks.get_json()
        assert tracks_data["status"] == "success"
        assert len(tracks_data["tracks"]) >= 1

        selected_track = tracks_data["tracks"][0]
        track_id = selected_track["id"]

        # Step 2: Track detail lookup
        res_track_detail = client.get(f"/api/v1/tracks/{track_id}")
        assert res_track_detail.status_code == 200
        track_detail = res_track_detail.get_json()
        assert track_detail["status"] == "success"
        topics = track_detail["track"]["topics"]
        assert len(topics) >= 2

        # Choose the first topic as known topic to test known-topic filtering
        known_topic_name = topics[0]["name"]
        known_topic_id = topics[0]["id"]
        unknown_topics = [t for t in topics if t["id"] != known_topic_id]

        # Step 3: Goal onboarding with known topics
        target_date_str = (date.today() + timedelta(days=60)).strftime("%d/%m/%Y")
        res_goal = client.post(
            "/api/v1/goals",
            headers=auth_headers,
            json={
                "track_id": track_id,
                "skill_level": "intermediate",
                "study_hours_per_day": 2.5,
                "target_date": target_date_str,
                "known_topics": [known_topic_name],
                "commitment": True,
            }
        )
        assert res_goal.status_code == 201
        goal_data = res_goal.get_json()["goal"]
        goal_id = goal_data["id"]
        assert goal_data["known_topics"] == [known_topic_name]

        # Step 4: Roadmap generation
        res_gen = client.post(
            "/api/v1/roadmap/generate",
            headers=auth_headers,
            json={"goal_id": goal_id}
        )
        assert res_gen.status_code == 200
        gen_data = res_gen.get_json()
        assert gen_data["status"] == "success"
        assert "roadmap_id" in gen_data

        # Verify known topic is excluded from the generated roadmap items
        daily_plan = gen_data["roadmap"]
        topic_ids_in_roadmap = {task["topic_id"] for day in daily_plan for task in day["tasks"]}
        assert known_topic_id not in topic_ids_in_roadmap, "Known topic should be excluded from generated roadmap!"

        # Step 5: Active roadmap load
        res_active_roadmap = client.get(
            f"/api/v1/roadmap/active?goal_id={goal_id}",
            headers=auth_headers
        )
        assert res_active_roadmap.status_code == 200
        active_rdmp_data = res_active_roadmap.get_json()
        assert active_rdmp_data["status"] == "success"
        assert active_rdmp_data["goal"]["id"] == goal_id
        assert active_rdmp_data["roadmap_id"] == gen_data["roadmap_id"]
        assert len(active_rdmp_data["roadmap"]) > 0

        # Step 6: Today's tasks retrieval (Day 1)
        res_tasks = client.get(
            f"/api/v1/tasks/today?goal_id={goal_id}",
            headers=auth_headers
        )
        assert res_tasks.status_code == 200
        tasks_data = res_tasks.get_json()
        assert tasks_data["status"] == "success"
        assert "tasks" in tasks_data
        todays_tasks = tasks_data["tasks"]
        assert len(todays_tasks) > 0

        first_task = todays_tasks[0]
        first_task_id = first_task["id"]
        assert first_task["status"] == "pending"

        # Step 7: Complete the first task
        res_complete = client.post(
            f"/api/v1/tasks/{first_task_id}/complete",
            headers=auth_headers,
            json={"actual_minutes": 45}
        )
        assert res_complete.status_code == 200
        complete_data = res_complete.get_json()
        assert complete_data["status"] == "success"
        assert complete_data["task"]["status"] == "completed"

        # Step 8: Swap resource for an item
        available_alts = first_task.get("available_resources", [])
        if available_alts:
            alt_res = available_alts[0]
            res_swap = client.put(
                f"/api/v1/roadmap-items/{first_task_id}/resource",
                headers=auth_headers,
                json={"resource_id": alt_res["id"]}
            )
            assert res_swap.status_code == 200
            swap_data = res_swap.get_json()
            assert swap_data["status"] == "success"
            assert swap_data["resource"]["id"] == alt_res["id"]

        # Step 9: Progress summary check
        res_prog = client.get(
            f"/api/v1/progress/summary?goal_id={goal_id}",
            headers=auth_headers
        )
        assert res_prog.status_code == 200
        prog_data = res_prog.get_json()
        assert prog_data["status"] == "success"
        assert prog_data["summary"]["completed_tasks"] >= 1
        assert prog_data["summary"]["completion_percentage"] > 0

        # Step 10: Skip another task if available
        if len(todays_tasks) > 1:
            second_task_id = todays_tasks[1]["id"]
            res_skip = client.post(
                f"/api/v1/tasks/{second_task_id}/skip",
                headers=auth_headers
            )
            assert res_skip.status_code == 200
            assert res_skip.get_json()["task"]["status"] == "skipped"

        # Step 11: Adaptive rescheduling with simulated date
        simulated_date = (date.today() + timedelta(days=3)).isoformat()
        res_reschedule = client.post(
            "/api/v1/roadmap/reschedule",
            headers=auth_headers,
            json={
                "goal_id": goal_id,
                "date": simulated_date,
                "preview": False
            }
        )
        assert res_reschedule.status_code == 200
        reschedule_data = res_reschedule.get_json()
        assert reschedule_data["status"] == "success"
        assert reschedule_data.get("replanned") is True, f"Not replanned: {reschedule_data}"
        assert reschedule_data["roadmap_version"] > 1

        # Step 12: Weekly reflections verification on Day 7
        res_refl_status = client.get(
            f"/api/v1/reflections/status?goal_id={goal_id}&day=7",
            headers=auth_headers
        )
        assert res_refl_status.status_code == 200
        refl_status_data = res_refl_status.get_json()
        assert refl_status_data["status"] == "success"
        assert refl_status_data["is_due"] is True
        assert refl_status_data["week_number"] == 1

        # Submit weekly reflection
        res_submit_refl = client.post(
            "/api/v1/reflections",
            headers=auth_headers,
            json={
                "goal_id": goal_id,
                "study_day": 7,
                "confidence_level": 5,
                "difficulty_rating": 2,
                "notes": "End-to-end journey verified! Concept retention is high."
            }
        )
        assert res_submit_refl.status_code == 201
        submit_data = res_submit_refl.get_json()
        assert submit_data["status"] == "success"
        assert submit_data["reflection"]["confidence_level"] == 5

        # Verify reflection is in the history log
        res_list_refl = client.get(
            f"/api/v1/reflections?goal_id={goal_id}",
            headers=auth_headers
        )
        assert res_list_refl.status_code == 200
        list_refl_data = res_list_refl.get_json()
        assert list_refl_data["status"] == "success"
        assert len(list_refl_data["reflections"]) >= 1
        assert list_refl_data["reflections"][0]["notes"] == "End-to-end journey verified! Concept retention is high."
