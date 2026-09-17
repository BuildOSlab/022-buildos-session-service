"""Database repository for BuildOS authenticated sessions."""

# Standard library imports
import uuid

# SQLAlchemy imports
from sqlalchemy.orm import Session

# Application imports
from app.models.session import UserSession


# Session repository
class SessionRepository:
    """Provide database access for authenticated session records."""

    # Repository initialization
    def __init__(self, db: Session) -> None:
        """Initialize the repository with a database session."""

        # Store the database session for repository operations.
        self.db = db

    # Create session
    def create(self, session: UserSession) -> UserSession:
        """Persist a new authenticated session."""

        # Add the session entity to the current transaction.
        self.db.add(session)

        # Commit the new session to the database.
        self.db.commit()

        # Refresh the entity so generated database values are available.
        self.db.refresh(session)

        # Return the persisted session entity.
        return session

    # Get session by ID
    def get_by_id(self, session_id: uuid.UUID) -> UserSession | None:
        """Return a session by its identifier."""

        # Query the session using its primary key.
        return (
            self.db.query(UserSession)
            .filter(UserSession.session_id == session_id)
            .first()
        )

    # Get sessions by user ID
    def get_by_user_id(self, user_id: uuid.UUID) -> list[UserSession]:
        """Return all sessions belonging to a user."""

        # Query sessions belonging to the specified user.
        return (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id)
            .all()
        )

    # Update session
    def update(self, session: UserSession) -> UserSession:
        """Persist changes to an existing session."""

        # Commit the updated session within the current transaction.
        self.db.commit()

        # Refresh the entity so the repository returns current database state.
        self.db.refresh(session)

        # Return the updated session entity.
        return session
