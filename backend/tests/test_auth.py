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
from models import User, Goal, Track, Roadmap, RoadmapItem, WeeklyReflection
from tests.jwt_test_helpers import (
    make_test_jwt,
    make_expired_jwt,
    make_forged_jwt,
    get_auth_headers,
    get_test_public_pem,
)


def test_authenticated_request_with_verified_clerk_token():
    """
    1. Valid verified authentication:
    A valid RS256 token signed with the matching key is accepted,
    resolves the user in the database, and stores profile info.
    """
    app = create_app()
    clerk_id = "user_clerk_verified_101"
    headers = get_auth_headers(sub=clerk_id, email="alice.verified@skillsprint.ai", name="Alice Verified")

    with app.test_client() as client:
        res = client.get("/api/v1/health", headers=headers)
        assert res.status_code == 200

        with app.app_context():
            user = User.query.filter_by(clerk_user_id=clerk_id).first()
            assert user is not None
            assert user.email == "alice.verified@skillsprint.ai"
            assert user.name == "Alice Verified"


def test_token_verification_failures_rejected_with_401():
    """
    2. Missing, malformed, expired, forged, and invalid-signature tokens:
    All invalid tokens must be rejected with HTTP 401 Unauthorized.
    """
    app = create_app()

    with app.test_client() as client:
        # A. Malformed token structure (not 3 period-separated parts)
        res_malformed = client.get("/api/v1/health", headers={"Authorization": "Bearer not.a.valid.jwt"})
        assert res_malformed.status_code == 401
        assert "malformed" in res_malformed.get_json()["message"].lower() or "invalid" in res_malformed.get_json()["message"].lower()

        # B. Corrupt / empty Bearer token
        res_empty = client.get("/api/v1/health", headers={"Authorization": "Bearer "})
        assert res_empty.status_code == 401

        # C. Invalid authorization scheme (e.g. Basic instead of Bearer)
        res_scheme = client.get("/api/v1/health", headers={"Authorization": "Basic dXNlcjpwYXNz"})
        assert res_scheme.status_code == 401
        assert "bearer token required" in res_scheme.get_json()["message"].lower()

        # D. Expired token
        expired_token = make_expired_jwt(sub="user_expired_test")
        res_expired = client.get("/api/v1/health", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_expired.status_code == 401
        assert "expired" in res_expired.get_json()["message"].lower()

        # E. Forged token (signed with an untrusted RSA private key)
        forged_token = make_forged_jwt(sub="user_attacker_forged")
        res_forged = client.get("/api/v1/health", headers={"Authorization": f"Bearer {forged_token}"})
        assert res_forged.status_code == 401
        assert "signature" in res_forged.get_json()["message"].lower()


def test_rejection_of_spoofed_x_clerk_headers():
    """
    3. Rejection of spoofed X-Clerk-User-Id / X-User-Id headers:
    Raw headers must NEVER be trusted as proof of identity.
    """
    app = create_app()

    with app.app_context():
        user_victim = User.query.filter_by(clerk_user_id="user_victim_clerk").first()
        if not user_victim:
            user_victim = User(clerk_user_id="user_victim_clerk", email="victim@example.com", name="Victim")
            db.session.add(user_victim)
            db.session.commit()

        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        victim_headers = get_auth_headers(sub="user_victim_clerk")

        with app.test_client() as client:
            # Create a goal for Victim
            res_v = client.post(
                "/api/v1/goals",
                headers=victim_headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2,
                    "target_date": target,
                    "commitment": True,
                }
            )
            assert res_v.status_code == 201
            victim_goal_id = res_v.get_json()["goal"]["id"]

            # Attacker attempts to access Victim's goal using only X-Clerk-User-Id header -> 401 Unauthorized
            res_spoof = client.get(
                f"/api/v1/goals/{victim_goal_id}",
                headers={"X-Clerk-User-Id": "user_victim_clerk"}
            )
            assert res_spoof.status_code == 401
            assert "authentication required" in res_spoof.get_json()["message"].lower()

            # Attacker sends their own valid token, but includes X-Clerk-User-Id: user_victim_clerk -> 403 Forbidden
            attacker_headers = get_auth_headers(sub="user_attacker_clerk")
            attacker_headers["X-Clerk-User-Id"] = "user_victim_clerk"
            res_cross = client.get(
                f"/api/v1/goals/{victim_goal_id}",
                headers=attacker_headers
            )
            assert res_cross.status_code == 403
            assert "denied" in res_cross.get_json()["message"].lower()


def test_anonymous_access_to_protected_endpoints_rejected():
    """
    4. Anonymous access to protected endpoints:
    Protected endpoints must reject unauthenticated requests with HTTP 401.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        headers = get_auth_headers(sub="user_auth_baseline")

        with app.test_client() as client:
            res_create = client.post(
                "/api/v1/goals",
                headers=headers,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2,
                    "target_date": target,
                    "commitment": True,
                }
            )
            assert res_create.status_code == 201
            goal_id = res_create.get_json()["goal"]["id"]

            # Generate roadmap
            client.post("/api/v1/roadmap/generate", headers=headers, json={"goal_id": goal_id})

            # Protected endpoints without Authorization header must return 401
            assert client.post("/api/v1/goals", json={"track_id": track.id}).status_code == 401
            assert client.get("/api/v1/goals/active").status_code == 401
            assert client.get(f"/api/v1/goals/{goal_id}").status_code == 401
            assert client.post("/api/v1/roadmap/generate", json={"goal_id": goal_id}).status_code == 401
            assert client.get(f"/api/v1/roadmap/active?goal_id={goal_id}").status_code == 401
            assert client.post("/api/v1/roadmap/reschedule", json={"goal_id": goal_id}).status_code == 401
            assert client.get(f"/api/v1/tasks/today?goal_id={goal_id}").status_code == 401
            assert client.get(f"/api/v1/progress/summary?goal_id={goal_id}").status_code == 401
            assert client.get(f"/api/v1/reflections?goal_id={goal_id}").status_code == 401
            assert client.get(f"/api/v1/reflections/status?goal_id={goal_id}").status_code == 401


def test_cross_user_isolation_and_legitimate_owner_access():
    """
    5 & 6. Cross-user access rejected with 403; Legitimate owner allowed with 200.
    User A cannot view, reschedule, or modify User B's goals, tasks, roadmap, or reflections.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=45)).strftime("%d/%m/%Y")

        token_a = get_auth_headers(sub="user_clerk_isolation_A")
        token_b = get_auth_headers(sub="user_clerk_isolation_B")

        with app.test_client() as client:
            # 1. User A creates Goal A
            res_a = client.post(
                "/api/v1/goals",
                headers=token_a,
                json={
                    "track_id": track.id,
                    "skill_level": "beginner",
                    "study_hours_per_day": 2,
                    "target_date": target,
                    "commitment": True,
                }
            )
            assert res_a.status_code == 201
            goal_a_id = res_a.get_json()["goal"]["id"]

            # User A generates Roadmap A
            res_gen_a = client.post("/api/v1/roadmap/generate", headers=token_a, json={"goal_id": goal_a_id})
            assert res_gen_a.status_code == 200

            # 2. User B creates Goal B
            res_b = client.post(
                "/api/v1/goals",
                headers=token_b,
                json={
                    "track_id": track.id,
                    "skill_level": "intermediate",
                    "study_hours_per_day": 3,
                    "target_date": target,
                    "commitment": True,
                }
            )
            assert res_b.status_code == 201
            goal_b_id = res_b.get_json()["goal"]["id"]

            # User B generates Roadmap B
            res_gen_b = client.post("/api/v1/roadmap/generate", headers=token_b, json={"goal_id": goal_b_id})
            assert res_gen_b.status_code == 200

            # --- Legitimate Owner Access (User A accesses Goal A) -> 200 OK ---
            assert client.get(f"/api/v1/goals/{goal_a_id}", headers=token_a).status_code == 200
            assert client.get(f"/api/v1/roadmap/active?goal_id={goal_a_id}", headers=token_a).status_code == 200
            assert client.get(f"/api/v1/tasks/today?goal_id={goal_a_id}", headers=token_a).status_code == 200
            assert client.get(f"/api/v1/progress/summary?goal_id={goal_a_id}", headers=token_a).status_code == 200

            # --- Cross-User Attacks: User A attempts to access User B's resources -> 403 Forbidden ---
            res_cross_goal = client.get(f"/api/v1/goals/{goal_b_id}", headers=token_a)
            assert res_cross_goal.status_code == 403
            assert "denied" in res_cross_goal.get_json()["message"].lower()

            res_cross_rdmp = client.get(f"/api/v1/roadmap/active?goal_id={goal_b_id}", headers=token_a)
            assert res_cross_rdmp.status_code == 403

            res_cross_tasks = client.get(f"/api/v1/tasks/today?goal_id={goal_b_id}", headers=token_a)
            assert res_cross_tasks.status_code == 403

            res_cross_prog = client.get(f"/api/v1/progress/summary?goal_id={goal_b_id}", headers=token_a)
            assert res_cross_prog.status_code == 403

            res_cross_resched = client.post("/api/v1/roadmap/reschedule", headers=token_a, json={"goal_id": goal_b_id, "preview": True})
            assert res_cross_resched.status_code == 403

            res_cross_refl = client.get(f"/api/v1/reflections?goal_id={goal_b_id}", headers=token_a)
            assert res_cross_refl.status_code == 403

            # --- User B attempting to mutate User A's task -> 403 Forbidden ---
            roadmap_a = Roadmap.query.filter_by(goal_id=goal_a_id, status="active").first()
            assert roadmap_a is not None
            item_a = RoadmapItem.query.filter_by(roadmap_id=roadmap_a.id).first()
            assert item_a is not None

            res_cross_complete = client.post(f"/api/v1/tasks/{item_a.id}/complete", headers=token_b, json={})
            assert res_cross_complete.status_code == 403

            res_cross_skip = client.post(f"/api/v1/tasks/{item_a.id}/skip", headers=token_b, json={})
            assert res_cross_skip.status_code == 403

            res_cross_swap = client.put(f"/api/v1/roadmap-items/{item_a.id}/resource", headers=token_b, json={"resource_id": 101})
            assert res_cross_swap.status_code == 403


def test_public_health_and_catalog_endpoints():
    """
    7. Public health and catalog endpoints:
    Genuinely public endpoints remain accessible to anonymous callers and authenticated users.
    """
    app = create_app()
    auth_headers = get_auth_headers(sub="user_public_visitor")

    with app.test_client() as client:
        # Public health check
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/health", headers=auth_headers).status_code == 200

        # Public tracks catalog
        res_tracks_anon = client.get("/api/v1/tracks")
        assert res_tracks_anon.status_code == 200
        assert res_tracks_anon.get_json()["status"] == "success"

        res_tracks_auth = client.get("/api/v1/tracks", headers=auth_headers)
        assert res_tracks_auth.status_code == 200

        # Public track detail
        track = Track.query.first()
        if track:
            assert client.get(f"/api/v1/tracks/{track.id}").status_code == 200
            assert client.get(f"/api/v1/tracks/{track.slug}").status_code == 200

        # Public resources catalog
        assert client.get("/api/v1/resources").status_code == 200


def test_safe_handling_of_legacy_unowned_records():
    """
    8. Safe handling of legacy records without an owner:
    Records with user_id=None are neither leaked nor deleted nor silently claimed.
    - Anonymous requests return 401 Unauthorized.
    - Authenticated users return 403 Forbidden.
    - Legacy record remains untouched in the database.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        assert track is not None

        # Insert a legacy unowned goal directly into DB (representing old/unowned data)
        legacy_goal = Goal(
            user_id=None,
            track_id=track.id,
            skill_level="intermediate",
            study_hours_per_day=2.0,
            target_date=date.today() + timedelta(days=60),
            known_topics="",
            commitment=False,
            status="active"
        )
        db.session.add(legacy_goal)
        db.session.commit()
        legacy_goal_id = legacy_goal.id

        auth_headers = get_auth_headers(sub="user_authenticated_visitor")

        with app.test_client() as client:
            # Anonymous request to legacy record -> 401 Unauthorized
            res_anon = client.get(f"/api/v1/goals/{legacy_goal_id}")
            assert res_anon.status_code == 401

            # Authenticated user request to unowned legacy record -> 403 Forbidden
            res_auth = client.get(f"/api/v1/goals/{legacy_goal_id}", headers=auth_headers)
            assert res_auth.status_code == 403
            assert "no associated owner" in res_auth.get_json()["message"].lower() or "denied" in res_auth.get_json()["message"].lower()

            # Verify the legacy goal was NOT modified or silently assigned to the user
            db.session.expire_all()
            reloaded = db.session.get(Goal, legacy_goal_id)
            assert reloaded is not None
            assert reloaded.user_id is None  # Preserved as-is


def test_single_active_goal_per_user_isolation():
    """
    Single active goal rule:
    Creating a new active goal for User A supersedes User A's previous goal,
    but User B's active goal remains active.
    """
    app = create_app()

    with app.app_context():
        track = Track.query.first()
        target = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")

        token_a = get_auth_headers(sub="user_single_active_A")
        token_b = get_auth_headers(sub="user_single_active_B")

        with app.test_client() as client:
            # 1. User A creates Goal A1
            res_a1 = client.post("/api/v1/goals", headers=token_a, json={
                "track_id": track.id,
                "skill_level": "beginner",
                "study_hours_per_day": 1.0,
                "target_date": target,
                "commitment": True
            })
            assert res_a1.status_code == 201
            goal_a1_id = res_a1.get_json()["goal"]["id"]

            # 2. User B creates Goal B1
            res_b1 = client.post("/api/v1/goals", headers=token_b, json={
                "track_id": track.id,
                "skill_level": "intermediate",
                "study_hours_per_day": 2.0,
                "target_date": target,
                "commitment": True
            })
            assert res_b1.status_code == 201
            goal_b1_id = res_b1.get_json()["goal"]["id"]

            # 3. User A creates Goal A2 (supersedes Goal A1)
            res_a2 = client.post("/api/v1/goals", headers=token_a, json={
                "track_id": track.id,
                "skill_level": "advanced",
                "study_hours_per_day": 2.5,
                "target_date": target,
                "commitment": True
            })
            assert res_a2.status_code == 201
            goal_a2_id = res_a2.get_json()["goal"]["id"]

            # Verify in DB: Goal A1 is superseded, Goal A2 is active, Goal B1 remains active!
            db.session.expire_all()
            goal_a1 = db.session.get(Goal, goal_a1_id)
            goal_a2 = db.session.get(Goal, goal_a2_id)
            goal_b1 = db.session.get(Goal, goal_b1_id)

            assert goal_a1.status == "superseded"
            assert goal_a2.status == "active"
            assert goal_b1.status == "active"  # Untouched!


def test_active_goal_scoped_strictly_to_authenticated_user():
    """
    GET /api/v1/goals/active strictly returns the authenticated user's active goal,
    ignoring any query parameter attempting to request another user's goal.
    """
    app = create_app()

    with app.app_context():
        token_a = get_auth_headers(sub="user_single_active_A")
        token_b = get_auth_headers(sub="user_single_active_B")

        with app.test_client() as client:
            res_a = client.get("/api/v1/goals/active", headers=token_a)
            assert res_a.status_code == 200
            data_a = res_a.get_json()["goal"]

            res_b = client.get("/api/v1/goals/active", headers=token_b)
            assert res_b.status_code == 200
            data_b = res_b.get_json()["goal"]

            assert data_a["id"] != data_b["id"]
            assert data_a["user_id"] != data_b["user_id"]

            # User A passes ?user_id=<user_b_id> -> Still gets User A's goal
            res_spoof = client.get(f"/api/v1/goals/active?user_id={data_b['user_id']}", headers=token_a)
            assert res_spoof.status_code == 200
            assert res_spoof.get_json()["goal"]["id"] == data_a["id"]


def test_fail_closed_when_clerk_unconfigured():
    """
    Fail closed test:
    When no Clerk verification key or JWKS is configured,
    requests with tokens must fail closed with 401 Unauthorized.
    """
    app = create_app()
    token = make_test_jwt(sub="user_unconfigured_test")

    # Temporarily remove verification key env vars
    orig_key = os.environ.pop("CLERK_JWT_KEY", None)
    orig_pem = os.environ.pop("CLERK_PEM_PUBLIC_KEY", None)
    orig_jwks = os.environ.pop("CLERK_JWKS_URL", None)
    orig_api = os.environ.pop("CLERK_FRONTEND_API", None)
    orig_dom = os.environ.pop("CLERK_DOMAIN", None)

    try:
        with app.test_client() as client:
            res = client.get("/api/v1/health", headers={"Authorization": f"Bearer {token}"})
            assert res.status_code == 401
            assert "unconfigured" in res.get_json()["message"].lower()
    finally:
        if orig_key is not None:
            os.environ["CLERK_JWT_KEY"] = orig_key
        if orig_pem is not None:
            os.environ["CLERK_PEM_PUBLIC_KEY"] = orig_pem
        if orig_jwks is not None:
            os.environ["CLERK_JWKS_URL"] = orig_jwks
        if orig_api is not None:
            os.environ["CLERK_FRONTEND_API"] = orig_api
        if orig_dom is not None:
            os.environ["CLERK_DOMAIN"] = orig_dom
