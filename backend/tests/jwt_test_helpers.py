import time
import os
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate test RSA key pair once for test execution
_TEST_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

_TEST_PUBLIC_PEM = _TEST_PRIVATE_KEY.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")

# Generate an alternate untrusted RSA key for testing forged signatures
_FORGED_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Automatically set CLERK_JWT_KEY in environment for test processes
os.environ["CLERK_JWT_KEY"] = _TEST_PUBLIC_PEM


def get_test_public_pem() -> str:
    """Returns the test RSA public key in PEM format."""
    return _TEST_PUBLIC_PEM


def make_test_jwt(
    sub: str,
    email: str | None = None,
    name: str = "SkillSprint Tester",
    exp_offset: int = 3600,
    iss: str | None = None,
    aud: str | None = None,
    azp: str | None = None,
) -> str:
    """Creates a valid, cryptographically signed RS256 JWT using the test key."""
    now = int(time.time())
    user_email = email if email is not None else f"{sub}@skillsprint.ai"
    payload = {
        "sub": sub,
        "email": user_email,
        "name": name,
        "iat": now,
        "nbf": now - 10,
        "exp": now + exp_offset,
    }
    if iss:
        payload["iss"] = iss
    if aud:
        payload["aud"] = aud
    if azp:
        payload["azp"] = azp

    return jwt.encode(
        payload,
        _TEST_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": "skillsprint_test_key_1"}
    )


def make_expired_jwt(sub: str = "expired_user") -> str:
    """Creates an RS256 JWT that is already expired."""
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": f"{sub}@skillsprint.ai",
        "name": "Expired User",
        "iat": now - 7200,
        "nbf": now - 7200,
        "exp": now - 3600,  # Expired 1 hour ago
    }
    return jwt.encode(
        payload,
        _TEST_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": "skillsprint_test_key_1"}
    )


def make_forged_jwt(sub: str = "forged_user") -> str:
    """
    Creates an RS256 JWT signed with an untrusted, foreign RSA private key.
    Signature verification against the server's public key will fail.
    """
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": f"{sub}@skillsprint.ai",
        "name": "Forged Attacker",
        "iat": now,
        "nbf": now - 10,
        "exp": now + 3600,
    }
    return jwt.encode(
        payload,
        _FORGED_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": "foreign_untrusted_key"}
    )


def get_auth_headers(sub: str, email: str | None = None, name: str = "Test User") -> dict:
    """Returns standard Authorization headers with a verified Bearer token."""
    user_email = email if email is not None else f"{sub}@skillsprint.ai"
    token = make_test_jwt(sub=sub, email=user_email, name=name)
    return {"Authorization": f"Bearer {token}"}

