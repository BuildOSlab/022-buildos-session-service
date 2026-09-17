"""Tests for the BuildOS session API."""

# Standard library imports
import uuid
from datetime import datetime, timedelta, timezone

# FastAPI imports
from fastapi.testclient import TestClient

# Application imports
from app.api.dependencies import get_db
from app.core.config import settings
from app.main import app

settings.internal_api_key = "test_internal_api_key"
settings.service_id = "buildos-session-service"

# Test client
client = TestClient(app)


def get_test_db():
    """Provide a database session for API tests."""

    from app.db.session import SessionLocal

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


def build_create_payload() -> dict[str, str]:
    """Build a valid session creation payload."""

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return {
        "user_id": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4()),
        "expires_at": expires_at.isoformat(),
    }


def build_auth_headers() -> dict[str, str]:
    """Return valid internal service authentication headers."""

    return {
        "Authorization": "Bearer test_internal_api_key",
        "X-Service-ID": "buildos-auth-service",
    }


def test_health_check() -> None:
    """The health endpoint should report an available service."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Session creation authorization
# ---------------------------------------------------------------------------


def test_create_session_requires_authorization() -> None:
    """Session creation must reject unauthenticated callers."""

    response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
    )

    assert response.status_code == 401


def test_create_session_requires_valid_api_key() -> None:
    """Session creation must reject invalid API keys."""

    response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers={
            "Authorization": "Bearer wrong-key",
            "X-Service-ID": "buildos-auth-service",
        },
    )

    assert response.status_code == 401


def test_create_session_requires_service_id() -> None:
    """Session creation must reject requests without a service ID."""

    response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers={
            "Authorization": "Bearer test_internal_api_key",
        },
    )

    assert response.status_code == 401


def test_create_session_rejects_unauthorized_service_id() -> None:
    """Session creation must reject unknown internal services."""

    response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers={
            "Authorization": "Bearer test_internal_api_key",
            "X-Service-ID": "buildos-rogue-service",
        },
    )

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Session endpoint authorization
# ---------------------------------------------------------------------------


def test_get_session_requires_authorization() -> None:
    """Session retrieval must reject unauthenticated callers."""

    response = client.get(
        f"/api/v1/sessions/{uuid.uuid4()}",
    )

    assert response.status_code == 401


def test_update_session_activity_requires_authorization() -> None:
    """Session activity updates must reject unauthenticated callers."""

    response = client.post(
        f"/api/v1/sessions/{uuid.uuid4()}/activity",
        json={
            "current_time": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 401


def test_revoke_session_requires_authorization() -> None:
    """Session revocation must reject unauthenticated callers."""

    response = client.post(
        f"/api/v1/sessions/{uuid.uuid4()}/revoke",
        json={
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "reason": "user_logout",
        },
    )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Session creation
# ---------------------------------------------------------------------------


def test_create_session() -> None:
    """The API should create an authenticated session."""

    payload = build_create_payload()

    response = client.post(
        "/api/v1/sessions",
        json=payload,
        headers=build_auth_headers(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["session_id"] is not None
    assert data["user_id"] == payload["user_id"]
    assert data["device_id"] == payload["device_id"]
    assert data["status"] == "active"
    assert data["revoked_at"] is None
    assert data["revocation_reason"] is None


# ---------------------------------------------------------------------------
# Session retrieval
# ---------------------------------------------------------------------------


def test_get_session() -> None:
    """The API should return an existing session."""

    create_response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers=build_auth_headers(),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["session_id"]

    response = client.get(
        f"/api/v1/sessions/{session_id}",
        headers=build_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
    assert response.json()["status"] == "active"


def test_get_unknown_session_returns_404() -> None:
    """The API should return 404 for an unknown session."""

    response = client.get(
        f"/api/v1/sessions/{uuid.uuid4()}",
        headers=build_auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_invalid_session_id_returns_422() -> None:
    """The API should reject an invalid session identifier."""

    response = client.get(
        "/api/v1/sessions/not-a-uuid",
        headers=build_auth_headers(),
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Session activity
# ---------------------------------------------------------------------------


def test_update_session_activity() -> None:
    """The API should update activity for an active session."""

    create_response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers=build_auth_headers(),
    )

    assert create_response.status_code == 201

    data = create_response.json()
    session_id = data["session_id"]
    original_activity = data["last_activity_at"]

    current_time = datetime.now(timezone.utc) + timedelta(minutes=1)

    response = client.post(
        f"/api/v1/sessions/{session_id}/activity",
        json={
            "current_time": current_time.isoformat(),
        },
        headers=build_auth_headers(),
    )

    assert response.status_code == 200

    updated_data = response.json()

    assert updated_data["session_id"] == session_id
    assert updated_data["last_activity_at"] != original_activity
    assert updated_data["status"] == "active"


def test_update_unknown_session_returns_404() -> None:
    """The API should return 404 when updating an unknown session."""

    response = client.post(
        f"/api/v1/sessions/{uuid.uuid4()}/activity",
        json={
            "current_time": datetime.now(timezone.utc).isoformat(),
        },
        headers=build_auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


# ---------------------------------------------------------------------------
# Session revocation
# ---------------------------------------------------------------------------


def test_revoke_session() -> None:
    """The API should revoke an existing session."""

    create_response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers=build_auth_headers(),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["session_id"]
    revoked_at = datetime.now(timezone.utc)

    response = client.post(
        f"/api/v1/sessions/{session_id}/revoke",
        json={
            "revoked_at": revoked_at.isoformat(),
            "reason": "user_logout",
        },
        headers=build_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == session_id
    assert data["status"] == "revoked"
    assert data["revoked_at"] is not None
    assert data["revocation_reason"] == "user_logout"


def test_revoke_unknown_session_returns_404() -> None:
    """The API should return 404 when revoking an unknown session."""

    response = client.post(
        f"/api/v1/sessions/{uuid.uuid4()}/revoke",
        json={
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "reason": "user_logout",
        },
        headers=build_auth_headers(),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


# ---------------------------------------------------------------------------
# Revoked session behavior
# ---------------------------------------------------------------------------


def test_revoked_session_does_not_update_activity() -> None:
    """A revoked session should not record new activity."""

    create_response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers=build_auth_headers(),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["session_id"]
    original_activity = create_response.json()["last_activity_at"]

    revoke_response = client.post(
        f"/api/v1/sessions/{session_id}/revoke",
        json={
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "reason": "user_logout",
        },
        headers=build_auth_headers(),
    )

    assert revoke_response.status_code == 200

    activity_response = client.post(
        f"/api/v1/sessions/{session_id}/activity",
        json={
            "current_time": (
                datetime.now(timezone.utc) + timedelta(minutes=5)
            ).isoformat(),
        },
        headers=build_auth_headers(),
    )

    assert activity_response.status_code == 200

    data = activity_response.json()

    assert data["status"] == "revoked"
    assert data["last_activity_at"] == original_activity


def test_revoked_session_is_not_expired() -> None:
    """Expiration should not overwrite a revoked session."""

    create_response = client.post(
        "/api/v1/sessions",
        json=build_create_payload(),
        headers=build_auth_headers(),
    )

    assert create_response.status_code == 201

    session_id = create_response.json()["session_id"]

    revoke_response = client.post(
        f"/api/v1/sessions/{session_id}/revoke",
        json={
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "reason": "user_logout",
        },
        headers=build_auth_headers(),
    )

    assert revoke_response.status_code == 200
    assert revoke_response.json()["status"] == "revoked"
