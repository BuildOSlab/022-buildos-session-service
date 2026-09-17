"""Domain service for BuildOS authenticated session lifecycle."""

# Standard library imports
import uuid
from datetime import datetime

# Application imports
from app.models.session import UserSession


# Session service
class SessionService:
    """Coordinate authenticated session lifecycle operations."""

    # Session construction
    def build_session(
        self,
        user_id: uuid.UUID,
        device_id: uuid.UUID,
        created_at: datetime,
        expires_at: datetime,
    ) -> UserSession:
        """Build a new authenticated session without persisting it."""

        # Create the session entity with its initial lifecycle state.
        return UserSession(
            user_id=user_id,
            device_id=device_id,
            created_at=created_at,
            last_activity_at=created_at,
            expires_at=expires_at,
            status="active",
        )

    # Session expiration check
    def is_expired(
        self,
        session: UserSession,
        current_time: datetime,
    ) -> bool:
        """Return whether the session has reached its expiration time."""

        # A session is expired when the current time is at or after its expiry.
        return current_time >= session.expires_at

    # Session revocation
    def revoke_session(
        self,
        session: UserSession,
        revoked_at: datetime,
        reason: str,
    ) -> UserSession:
        """Mark an active session as revoked."""

        # Record when and why the session was invalidated.
        session.revoked_at = revoked_at
        session.revocation_reason = reason
        session.status = "revoked"

        # Return the updated session entity to the caller.
        return session

    # Session expiration
    def expire_session(
        self,
        session: UserSession,
        current_time: datetime,
    ) -> UserSession:
        """Mark an active session as expired when its lifetime has ended."""

        # Only active sessions can transition into the expired state.
        if session.status == "active" and self.is_expired(session, current_time):
            session.status = "expired"

        # Return the session with its updated lifecycle state.
        return session

    # Session activity update
    def update_activity(
        self,
        session: UserSession,
        current_time: datetime,
    ) -> UserSession:
        """Update the last activity time for an active session."""

        # Only active sessions can record new activity.
        if session.status == "active":
            session.last_activity_at = current_time

        # Return the updated session entity.
        return session
