"""Tests for the BuildOS session domain service."""

# Standard library imports
import uuid
from datetime import datetime, timedelta, timezone

# Application imports
from app.services.session_service import SessionService


# Session service fixture
def build_test_session():
    """Create a reusable session for service-layer tests."""

    service = SessionService()
    created_at = datetime.now(timezone.utc)

    return service.build_session(
        user_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        created_at=created_at,
        expires_at=created_at + timedelta(minutes=15),
    )


# Session construction tests
def test_build_session_creates_active_session() -> None:
    """A newly built session should start in the active state."""

    session = build_test_session()

    assert session.status == "active"
    assert session.revoked_at is None
    assert session.revocation_reason is None


# Expiration detection tests
def test_is_expired_returns_false_before_expiration() -> None:
    """An active session should not be expired before its expiry time."""

    service = SessionService()
    session = build_test_session()

    current_time = session.expires_at - timedelta(seconds=1)

    assert service.is_expired(session, current_time) is False


def test_is_expired_returns_true_at_expiration() -> None:
    """A session should be expired at its exact expiry time."""

    service = SessionService()
    session = build_test_session()

    assert service.is_expired(session, session.expires_at) is True


# Session expiration tests
def test_expire_session_changes_active_session_to_expired() -> None:
    """An expired active session should transition to expired."""

    service = SessionService()
    session = build_test_session()

    expired_session = service.expire_session(
        session,
        session.expires_at,
    )

    assert expired_session.status == "expired"


# Session activity tests
def test_update_activity_updates_active_session() -> None:
    """Updating activity should change the last activity time."""

    service = SessionService()
    session = build_test_session()

    current_time = session.created_at + timedelta(minutes=5)

    updated_session = service.update_activity(
        session,
        current_time,
    )

    assert updated_session.last_activity_at == current_time
    assert updated_session.status == "active"


def test_update_activity_does_not_update_revoked_session() -> None:
    """A revoked session should not record new activity."""

    service = SessionService()
    session = build_test_session()

    original_activity_time = session.last_activity_at
    session.status = "revoked"

    current_time = original_activity_time + timedelta(minutes=5)

    updated_session = service.update_activity(
        session,
        current_time,
    )

    assert updated_session.last_activity_at == original_activity_time
    assert updated_session.status == "revoked"


# Session revocation tests
def test_revoke_session_records_revocation_details() -> None:
    """Revoking a session should record its time, reason, and status."""

    service = SessionService()
    session = build_test_session()
    revoked_at = datetime.now(timezone.utc)

    revoked_session = service.revoke_session(
        session,
        revoked_at,
        "logout",
    )

    assert revoked_session.status == "revoked"
    assert revoked_session.revoked_at == revoked_at
    assert revoked_session.revocation_reason == "logout"
