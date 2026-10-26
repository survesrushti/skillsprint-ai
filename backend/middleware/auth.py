import os
import json
from functools import wraps
from flask import request, jsonify, g
import jwt
from jwt import PyJWKClient, PyJWTError, ExpiredSignatureError, InvalidSignatureError, DecodeError

from extensions import db
from models import User, Goal


# Cached JWKS clients keyed by JWKS URL
_JWKS_CLIENTS: dict[str, PyJWKClient] = {}


def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    """Returns a cached PyJWKClient for fetching and caching Clerk public keys."""
    if jwks_url not in _JWKS_CLIENTS:
        _JWKS_CLIENTS[jwks_url] = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
    return _JWKS_CLIENTS[jwks_url]


def _format_pem_key(key_str: str) -> str:
    """
    Normalizes a PEM key string from environment variables.
    Handles raw single-line base64 or multi-line PEM formatting with escaped newlines.
    """
    key = key_str.strip().replace("\\n", "\n")
    if "-----BEGIN PUBLIC KEY-----" in key:
        return key
    if "-----BEGIN RSA PUBLIC KEY-----" in key:
        return key

    # If key is provided as raw base64 string, wrap with standard PEM header and footer
    lines = [key[i:i + 64] for i in range(0, len(key), 64)]
    return "-----BEGIN PUBLIC KEY-----\n" + "\n".join(lines) + "\n-----END PUBLIC KEY-----\n"


def verify_clerk_token(token: str) -> tuple[dict | None, str | None]:
    """
    Cryptographically verifies a Clerk-issued JWT token.
    Supports:
      1. CLERK_JWT_KEY or CLERK_PEM_PUBLIC_KEY (local RS256 PEM public key)
      2. CLERK_JWKS_URL or CLERK_FRONTEND_API / CLERK_DOMAIN (JWKS endpoint)

    Validates:
      - RS256 algorithm
      - Cryptographic signature
      - Token expiration (exp)
      - Not before / Issued at (nbf / iat)
      - Issuer (iss) if CLERK_ISSUER or CLERK_FRONTEND_API is configured
      - Authorized parties (azp) or Audience (aud) if configured
      - Subject claim (sub) presence

    Returns:
      (payload: dict, None) on success
      (None, error_message: str) on failure (fails closed)
    """
    if not token or not isinstance(token, str):
        return None, "Authentication token is missing or empty."

    parts = token.strip().split(".")
    if len(parts) != 3:
        return None, "Invalid or malformed authentication token structure."

    pem_key_env = os.getenv("CLERK_JWT_KEY") or os.getenv("CLERK_PEM_PUBLIC_KEY")
    jwks_url_env = os.getenv("CLERK_JWKS_URL")
    clerk_domain = os.getenv("CLERK_FRONTEND_API") or os.getenv("CLERK_DOMAIN")

    signing_key = None

    if pem_key_env:
        try:
            signing_key = _format_pem_key(pem_key_env)
        except Exception:
            return None, "Invalid server configuration for token verification key."
    elif jwks_url_env or clerk_domain:
        jwks_url = jwks_url_env or f"https://{clerk_domain.rstrip('/')}/.well-known/jwks.json"
        try:
            client = _get_jwks_client(jwks_url)
            signing_key = client.get_signing_key_from_jwt(token).key
        except Exception as jwks_err:
            return None, f"Failed to retrieve verification key from JWKS: {str(jwks_err)}"
    else:
        # Fail closed: No verification key or JWKS URL configured
        return None, "Authentication service is unconfigured (missing Clerk verification key or JWKS)."

    decode_options = {
        "verify_signature": True,
        "require": ["exp", "sub"],
    }

    expected_issuer = os.getenv("CLERK_ISSUER")
    expected_aud = os.getenv("CLERK_AUDIENCE")
    authorized_parties = os.getenv("CLERK_AUTHORIZED_PARTIES")

    try:
        kwargs: dict = {
            "algorithms": ["RS256"],
            "options": decode_options,
        }
        if expected_issuer:
            kwargs["issuer"] = expected_issuer
        if expected_aud:
            kwargs["audience"] = expected_aud

        payload = jwt.decode(token, signing_key, **kwargs)

        # Validate authorized party (azp) if configured
        if authorized_parties:
            allowed_azp = [p.strip() for p in authorized_parties.split(",") if p.strip()]
            token_azp = payload.get("azp")
            if token_azp not in allowed_azp:
                return None, f"Unauthorized token party (azp '{token_azp}' not allowed)."

        sub = payload.get("sub")
        if not sub or not isinstance(sub, str) or not sub.strip():
            return None, "Token payload is missing a valid subject identity (sub)."

        return payload, None

    except ExpiredSignatureError:
        return None, "Authentication token has expired. Please sign in again."
    except InvalidSignatureError:
        return None, "Invalid token signature. Authentication rejected."
    except DecodeError:
        return None, "Invalid or malformed authentication token."
    except PyJWTError as err:
        return None, f"Authentication token verification failed: {str(err)}"
    except Exception as err:
        return None, f"Unexpected error during token verification: {str(err)}"


def extract_clerk_identity(req) -> tuple[str | None, str | None, str | None, str | None]:
    """
    Extracts verified (clerk_user_id, email, name, auth_error) from the request.
    Identity is obtained ONLY from a cryptographically verified Bearer token.
    Raw X-Clerk-User-Id / X-User-Id headers are NEVER trusted as proof of identity.
    """
    auth_header = req.headers.get("Authorization", "").strip()
    if not auth_header:
        # Anonymous request
        return None, None, None, None

    if not auth_header.startswith("Bearer "):
        return None, None, None, "Invalid authorization scheme. Bearer token required."

    token = auth_header[7:].strip()
    if not token:
        return None, None, None, "Authorization token is missing."

    payload, verify_err = verify_clerk_token(token)
    if verify_err:
        return None, None, None, verify_err

    clerk_id = payload.get("sub")
    email = payload.get("email") or payload.get("primary_email_address")
    first = payload.get("first_name", "")
    last = payload.get("last_name", "")
    if first or last:
        name = f"{first} {last}".strip()
    else:
        name = payload.get("name")

    return clerk_id, email, name, None


def get_or_create_user(clerk_user_id: str, email: str | None = None, name: str | None = None) -> User | None:
    """
    Resolves a verified clerk_user_id to a User model in the database.
    Creates a new user record on first visit or syncs updated metadata.
    """
    if not clerk_user_id:
        return None

    try:
        user = User.query.filter_by(clerk_user_id=clerk_user_id).first()
        if user is None:
            # Handle potential email collision gracefully to respect UNIQUE constraint
            if email:
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    email = None

            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                name=name,
            )
            db.session.add(user)
            db.session.commit()
        else:
            changed = False
            if email and user.email != email:
                existing_email = User.query.filter_by(email=email).first()
                if not existing_email:
                    user.email = email
                    changed = True
            if name and user.name != name:
                user.name = name
                changed = True
            if changed:
                db.session.commit()
        return user
    except Exception as err:
        db.session.rollback()
        print(f"[Auth] Notice: Could not resolve/create user record: {err}")
        return None


def authenticate_request():
    """
    Flask before_request hook.
    Populates g.current_user, g.user_id, g.clerk_user_id on successful authentication.
    If an Authorization header is provided but is invalid/expired/forged,
    rejects immediately with 401 Unauthorized.
    If no Authorization header is provided, leaves g.current_user=None (anonymous request),
    allowing public catalog/health endpoints to succeed and protected endpoints to enforce auth.
    """
    g.auth_error = None
    g.current_user = None
    g.user_id = None
    g.clerk_user_id = None

    clerk_id, email, name, auth_error = extract_clerk_identity(request)
    if auth_error:
        g.auth_error = auth_error
        return jsonify({
            "status": "error",
            "message": auth_error
        }), 401

    if clerk_id:
        user = get_or_create_user(clerk_id, email=email, name=name)
        if user:
            g.current_user = user
            g.user_id = user.id
            g.clerk_user_id = user.clerk_user_id
        else:
            g.auth_error = "Could not resolve user account."
            return jsonify({
                "status": "error",
                "message": "Could not resolve user account."
            }), 401


def require_auth(f):
    """
    Route decorator requiring valid user authentication.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if getattr(g, "auth_error", None):
            return jsonify({
                "status": "error",
                "message": g.auth_error
            }), 401

        current_uid = getattr(g, "user_id", None)
        if current_uid is None:
            return jsonify({
                "status": "error",
                "message": "Authentication required. Please sign in."
            }), 401

        return f(*args, **kwargs)
    return decorated


def check_goal_access(goal: Goal | None) -> tuple[bool, str | None]:
    """
    Verifies that the authenticated user has permission to access this goal.
    Enforces strict ownership:
      - Anonymous callers are rejected with 'Authentication required to access this goal.' (401).
      - Legacy or unowned records (goal.user_id is None) are rejected with
        'Access denied. This goal has no associated owner.' (403) without mutating or deleting them.
      - Another user's goal is rejected with 'Access denied. You do not have permission to view or modify this goal.' (403).
      - Genuine owner (goal.user_id == g.user_id) is allowed (True, None).
    """
    auth_err = getattr(g, "auth_error", None)
    if auth_err:
        return False, auth_err

    current_uid = getattr(g, "user_id", None)
    if current_uid is None:
        return False, "Authentication required to access this goal."

    if goal is None:
        return False, "Goal not found."

    # Legacy records without an assigned owner
    if goal.user_id is None:
        return False, "Access denied. This goal has no associated owner."

    # Cross-user isolation check
    if goal.user_id != current_uid:
        return False, "Access denied. You do not have permission to view or modify this goal."

    return True, None


def get_current_user_id() -> int | None:
    """Returns the database integer user_id of the authenticated user, or None."""
    return getattr(g, "user_id", None)
