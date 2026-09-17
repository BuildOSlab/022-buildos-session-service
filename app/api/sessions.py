"""FastAPI routes for BuildOS authenticated sessions."""
# ruff: noqa: B008

# Standard library imports
import uuid
from datetime import datetime, timezone

# FastAPI imports
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy imports
from sqlalchemy.orm import Session

# Application imports
from app.api.dependencies import get_db, verify_internal_service
from app.models.session import UserSession
from app.repositories.session_repository import SessionRepository
from app.schemas.session import (
    SessionActivityRequest,
    SessionCreateRequest,
    SessionResponse,
    SessionRevokeRequest,
)
from app.services.session_service import SessionService

# Session API router
router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["sessions"],
)


# Create session
@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    request: SessionCreateRequest,
    _: bool = Depends(verify_internal_service),
    db: Session = Depends(get_db),
) -> UserSession:
    """Create and persist an authenticated session."""

    repository = SessionRepository(db)
    service = SessionService()
    created_at = datetime.now(timezone.utc)

    session = service.build_session(
        user_id=request.user_id,
        device_id=request.device_id,
        created_at=created_at,
        expires_at=request.expires_at,
    )

    return repository.create(session)


# Get session
@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
def get_session(
    session_id: uuid.UUID,
    _: bool = Depends(verify_internal_service),
    db: Session = Depends(get_db),
) -> UserSession:
    """Return an authenticated session by identifier."""

    repository = SessionRepository(db)
    session = repository.get_by_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


# Update session activity
@router.post(
    "/{session_id}/activity",
    response_model=SessionResponse,
)
def update_session_activity(
    session_id: uuid.UUID,
    request: SessionActivityRequest,
    _: bool = Depends(verify_internal_service),
    db: Session = Depends(get_db),
) -> UserSession:
    """Record activity for an authenticated session."""

    repository = SessionRepository(db)
    service = SessionService()
    session = repository.get_by_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    updated_session = service.update_activity(
        session,
        request.current_time,
    )

    return repository.update(updated_session)


# Revoke session
@router.post(
    "/{session_id}/revoke",
    response_model=SessionResponse,
)
def revoke_session(
    session_id: uuid.UUID,
    request: SessionRevokeRequest,
    _: bool = Depends(verify_internal_service),
    db: Session = Depends(get_db),
) -> UserSession:
    """Revoke an authenticated session."""

    repository = SessionRepository(db)
    service = SessionService()
    session = repository.get_by_id(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    revoked_session = service.revoke_session(
        session,
        request.revoked_at,
        request.reason,
    )

    return repository.update(revoked_session)

