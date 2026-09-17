"""Tests for the BuildOS session repository."""

# Standard library imports
import uuid
from datetime import datetime, timedelta, timezone

# Application imports
from app.db.session import SessionLocal
from app.models.session import UserSession
from app.repositories.session_repository import SessionRepository


def get_test_db():
    """Provide a database session for repository tests."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def build_test_session(user_id: uuid.UUID | None = None) -> UserSession:
    """Create an unsaved session entity for repository tests."""

    created_at = datetime.now(timezone.utc)

    return UserSession(
        user_id=user_id or uuid.uuid4(),
        device_id=uuid.uuid4(),
        created_at=created_at,
        last_activity_at=created_at,
        expires_at=created_at + timedelta(minutes=15),
        status="active",
    )


def test_create_persists_session() -> None:
    """The repository should persist a new session."""

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        repository = SessionRepository(db)
        session = build_test_session()

        saved_session = repository.create(session)

        assert saved_session.session_id is not None
        assert saved_session.user_id == session.user_id
        assert saved_session.device_id == session.device_id
        assert saved_session.status == "active"

        persisted_session = (
            db.query(UserSession)
            .filter(UserSession.session_id == saved_session.session_id)
            .one()
        )

        assert persisted_session.user_id == session.user_id
        assert persisted_session.status == "active"

    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass


def test_get_by_user_id_returns_user_sessions() -> None:
    """The repository should return all sessions belonging to a user."""

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        repository = SessionRepository(db)
        user_id = uuid.uuid4()

        session_one = repository.create(build_test_session(user_id))
        session_two = repository.create(build_test_session(user_id))

        sessions = repository.get_by_user_id(user_id)

        session_ids = {session.session_id for session in sessions}

        assert session_one.session_id in session_ids
        assert session_two.session_id in session_ids

    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass


def test_get_by_user_id_does_not_return_other_users_sessions() -> None:
    """The repository should isolate sessions by user ID."""

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        repository = SessionRepository(db)

        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        user_session = repository.create(build_test_session(user_id))
        other_session = repository.create(build_test_session(other_user_id))

        sessions = repository.get_by_user_id(user_id)

        session_ids = {session.session_id for session in sessions}

        assert user_session.session_id in session_ids
        assert other_session.session_id not in session_ids

    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass


def test_update_persists_session_changes() -> None:
    """The repository should persist changes to an existing session."""

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        repository = SessionRepository(db)
        session = repository.create(build_test_session())

        session.status = "revoked"
        session.revoked_at = datetime.now(timezone.utc)
        session.revocation_reason = "user_logout"

        updated_session = repository.update(session)

        assert updated_session.status == "revoked"
        assert updated_session.revoked_at is not None
        assert updated_session.revocation_reason == "user_logout"

        persisted_session = (
            db.query(UserSession)
            .filter(UserSession.session_id == session.session_id)
            .one()
        )

        assert persisted_session.status == "revoked"
        assert persisted_session.revoked_at is not None
        assert persisted_session.revocation_reason == "user_logout"

    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass

def test_get_by_id_returns_session() -> None:
    """The repository should return a session by its identifier."""

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        repository = SessionRepository(db)
        session = repository.create(build_test_session())

        result = repository.get_by_id(session.session_id)

        assert result is not None
        assert result.session_id == session.session_id
        assert result.user_id == session.user_id
        assert result.device_id == session.device_id

    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass


def test_get_by_id_returns_none_for_unknown_session() -> None:
    """The repository should return None for an unknown session identifier."""

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        repository = SessionRepository(db)

        result = repository.get_by_id(uuid.uuid4())

        assert result is None

    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass
