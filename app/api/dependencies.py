"""FastAPI dependencies for the BuildOS Session Service."""

from collections.abc import Generator

from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal

internal_api_key_header = APIKeyHeader(
    name="Authorization",
    auto_error=False,
)


async def verify_internal_service(
    api_key: str | None = Security(internal_api_key_header),
    service_id: str | None = Header(
        default=None,
        alias="X-Service-ID",
    ),
) -> bool:
    """Verify internal BuildOS service authentication."""

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key.",
        )

    if not service_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing service identity.",
        )

    if api_key.startswith("Bearer "):
        api_key = api_key.removeprefix("Bearer ").strip()

    if not settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Internal service API key is not configured.",
        )

    if api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    if service_id != "buildos-auth-service":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized service.",
        )

    return True


# Database dependency
def get_db() -> Generator[Session, None, None]:
    """Provide a database session for an API request."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
