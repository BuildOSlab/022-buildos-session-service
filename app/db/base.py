"""SQLAlchemy declarative base and model metadata."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


from app.models.device import UserDevice
from app.models.session import UserSession

__all__ = ["Base", "UserDevice", "UserSession"]
