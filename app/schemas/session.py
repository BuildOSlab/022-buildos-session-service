"""Pydantic schemas for BuildOS authenticated sessions."""

# pylint: disable=too-few-public-methods
# Standard library imports
import uuid
from datetime import datetime

# Pydantic imports
from pydantic import BaseModel, ConfigDict


# Create session request
class SessionCreateRequest(BaseModel):
    """Request payload for creating an authenticated session."""

    user_id: uuid.UUID
    device_id: uuid.UUID
    expires_at: datetime


# Session response
class SessionResponse(BaseModel):
    """Response payload representing an authenticated session."""

    model_config = ConfigDict(from_attributes=True)

    session_id: uuid.UUID
    user_id: uuid.UUID
    device_id: uuid.UUID
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    status: str
    revocation_reason: str | None


# Session activity request
class SessionActivityRequest(BaseModel):
    """Request payload for recording session activity."""

    current_time: datetime


# Session revoke request
class SessionRevokeRequest(BaseModel):
    """Request payload for revoking an authenticated session."""

    revoked_at: datetime
    reason: str
