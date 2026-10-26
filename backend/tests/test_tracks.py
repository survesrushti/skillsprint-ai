import os
import sys

# Ensure backend directory is in sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import create_app
from extensions import db
from models import Track


def test_get_all_tracks():
    app = create_app()

    with app.test_client() as client:
        res = client.get("/api/v1/tracks")
        assert res.status_code == 200

        data = res.get_json()
        assert data["status"] == "success"
        assert data["count"] >= 3
        assert len(data["tracks"]) >= 3

        track_slugs = [t["slug"] for t in data["tracks"]]
        assert "full-stack-development" in track_slugs
        assert "data-analytics" in track_slugs
        assert "ui-ux-design" in track_slugs

        for track in data["tracks"]:
            assert "id" in track
            assert "name" in track
            assert "slug" in track
            assert "description" in track
            assert "topic_count" in track
            assert "total_minutes" in track
            assert "topics" in track
            assert isinstance(track["topics"], list)
            assert track["topic_count"] == len(track["topics"])
            assert track["total_minutes"] > 0

            # Check topic serialization details
            for topic in track["topics"]:
                assert "id" in topic
                assert "name" in topic
                assert "slug" in topic
                assert "estimated_minutes" in topic
                assert "difficulty" in topic
                assert "priority" in topic
                assert "is_optional" in topic
                assert "prerequisites" in topic
                assert isinstance(topic["prerequisites"], list)


def test_get_track_by_canonical_slug():
    app = create_app()

    with app.test_client() as client:
        res = client.get("/api/v1/tracks/full-stack-development")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["track"]["slug"] == "full-stack-development"
        assert data["track"]["name"] == "Full Stack Development"
        assert len(data["track"]["topics"]) > 0

        res_da = client.get("/api/v1/tracks/data-analytics")
        assert res_da.status_code == 200
        assert res_da.get_json()["track"]["slug"] == "data-analytics"

        res_ui = client.get("/api/v1/tracks/ui-ux-design")
        assert res_ui.status_code == 200
        assert res_ui.get_json()["track"]["slug"] == "ui-ux-design"


def test_get_track_by_alias():
    app = create_app()

    with app.test_client() as client:
        # 'full-stack' alias
        res_fs = client.get("/api/v1/tracks/full-stack")
        assert res_fs.status_code == 200
        data_fs = res_fs.get_json()
        assert data_fs["status"] == "success"
        assert data_fs["track"]["slug"] == "full-stack-development"

        # 'ui-ux' alias
        res_ui = client.get("/api/v1/tracks/ui-ux")
        assert res_ui.status_code == 200
        data_ui = res_ui.get_json()
        assert data_ui["status"] == "success"
        assert data_ui["track"]["slug"] == "ui-ux-design"


def test_get_track_by_numeric_id():
    app = create_app()

    with app.test_client() as client:
        res = client.get("/api/v1/tracks/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["track"]["id"] == 1


def test_get_track_not_found():
    app = create_app()

    with app.test_client() as client:
        res = client.get("/api/v1/tracks/non-existent-track-xyz")
        assert res.status_code == 404
        data = res.get_json()
        assert data["status"] == "error"
        assert "not found" in data["message"].lower()

