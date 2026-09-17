"""FastAPI application for the BuildOS Session Service."""

from fastapi import FastAPI

from app.api.sessions import router as sessions_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


# Session API routes
app.include_router(sessions_router)


# Health check
@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the health status of the session service."""

    return {"status": "ok"}
