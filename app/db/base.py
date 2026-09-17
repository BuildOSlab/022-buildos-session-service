"""SQLAlchemy declarative base and model metadata."""
# pylint: disable=too-few-public-methods

# SQLAlchemy imports
from sqlalchemy.orm import DeclarativeBase


# Database model base
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
