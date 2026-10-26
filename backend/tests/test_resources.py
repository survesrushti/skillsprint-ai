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
from models import Resource, Topic, RoadmapItem, Roadmap, Goal, Track
from tests.jwt_test_helpers import get_auth_headers


def test_public_topic_resources_route():
    """Verify GET /api/v1/topics/<id>/resources returns curated and database resources."""
    app = create_app()

    with app.test_client() as client:
        # Topic 1 exists in seeds (HTML Fundamentals)
        res = client.get("/api/v1/topics/1/resources")
        assert res.status_code == 200

        data = res.get_json()
        assert data["status"] == "success"
        assert data["topic_id"] == 1
        assert "resources" in data
        assert len(data["resources"]) >= 1

        first_res = data["resources"][0]
        assert "title" in first_res
        assert "url" in first_res
        assert "resource_type" in first_res

        # Non-existent topic
        res_none = client.get("/api/v1/topics/999999/resources")
        assert res_none.status_code == 404


def test_public_resources_list_and_filter():
    """Verify GET /api/v1/resources with optional topic_id filter."""
    app = create_app()

    with app.test_client() as client:
        # Unfiltered list
        res_all = client.get("/api/v1/resources")
        assert res_all.status_code == 200
        all_data = res_all.get_json()
        assert all_data["status"] == "success"
        assert len(all_data["resources"]) >= 1

        # Filtered by topic_id=1
        res_filtered = client.get("/api/v1/resources?topic_id=1")
        assert res_filtered.status_code == 200
        filtered_data = res_filtered.get_json()
        for r in filtered_data["resources"]:
            assert r["topic_id"] == 1


def test_public_resource_by_id():
    """Verify GET /api/v1/resources/<id>."""
    app = create_app()

    with app.test_client() as client:
        # Resource 1 exists in seeds
        res = client.get("/api/v1/resources/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["resource"]["id"] == 1
        assert "MDN" in data["resource"]["title"]

        # Non-existent resource
        res_none = client.get("/api/v1/resources/888888")
        assert res_none.status_code == 404


def test_swap_item_resource_flow():
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        headers = get_auth_headers("resource_swap_user_flow")

        with app.test_client() as client:
            # Setup goal and roadmap for this authenticated user
            goal_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                }
            )
            assert goal_res.status_code == 201
            goal_id = goal_res.get_json()["goal"]["id"]

            rm_res = client.post("/api/v1/roadmap/generate", headers=headers, json={"goal_id": goal_id})
            assert rm_res.status_code == 200

            roadmap = Roadmap.query.filter_by(goal_id=goal_id, status="active").first()
            assert roadmap is not None
            item = RoadmapItem.query.filter_by(roadmap_id=roadmap.id).first()
            assert item is not None

            # Check available resources for this item's topic
            res_avail = client.get(f"/api/v1/topics/{item.topic_id}/resources", headers=headers)
            assert res_avail.status_code == 200
            avail_data = res_avail.get_json()["resources"]
            assert len(avail_data) >= 1

            # Pick a target resource
            target_res = avail_data[-1]

            # Execute swap
            res_swap = client.put(
                f"/api/v1/roadmap-items/{item.id}/resource",
                headers=headers,
                json={"resource_id": target_res["id"]}
            )
            assert res_swap.status_code == 200
            swap_data = res_swap.get_json()
            assert swap_data["status"] == "success"
            assert swap_data["resource"]["id"] == target_res["id"]
            assert swap_data["resource"]["title"] == target_res["title"]

            # Also verify /tasks/<id>/resource alias works
            res_alias = client.put(
                f"/api/v1/tasks/{item.id}/resource",
                headers=headers,
                json={"resource_id": target_res["id"]}
            )
            assert res_alias.status_code == 200


def test_swap_item_resource_validation():
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        headers = get_auth_headers("resource_swap_user_val")

        with app.test_client() as client:
            # 404 on non-existent item (with authentication)
            res_404 = client.put(
                "/api/v1/roadmap-items/99999999/resource",
                headers=headers,
                json={"resource_id": 1}
            )
            assert res_404.status_code == 404

            # Setup user goal and item
            goal_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                }
            )
            goal_id = goal_res.get_json()["goal"]["id"]
            client.post("/api/v1/roadmap/generate", headers=headers, json={"goal_id": goal_id})
            roadmap = Roadmap.query.filter_by(goal_id=goal_id, status="active").first()
            item = RoadmapItem.query.filter_by(roadmap_id=roadmap.id).first()
            assert item is not None

            # 400 on invalid resource for different topic
            other_res = Resource.query.filter(Resource.topic_id != item.topic_id).first()
            if other_res:
                res_400 = client.put(
                    f"/api/v1/roadmap-items/{item.id}/resource",
                    headers=headers,
                    json={"resource_id": other_res.id}
                )
                assert res_400.status_code == 400
                assert "not valid for topic" in res_400.get_json()["message"]


def test_today_tasks_includes_resource_and_available_options():
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        headers = get_auth_headers("resource_swap_user_tasks")

        with app.test_client() as client:
            goal_res = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2.0,
                    "target_date": target,
                    "commitment": True,
                }
            )
            goal_id = goal_res.get_json()["goal"]["id"]
            client.post("/api/v1/roadmap/generate", headers=headers, json={"goal_id": goal_id})

            res = client.get(f"/api/v1/tasks/today?goal_id={goal_id}", headers=headers)
            assert res.status_code == 200
            data = res.get_json()
            for task in data["tasks"]:
                assert "resource" in task
                assert "available_resources" in task
                assert isinstance(task["available_resources"], list)
                if task["resource"]:
                    assert "title" in task["resource"]
                    assert "url" in task["resource"]
                    assert "resource_type" in task["resource"]
