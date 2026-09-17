"""Run database migrations and verify the Session Service schema."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.session import engine


EXPECTED_TABLES = {"user_sessions"}
EXPECTED_REVISION = "800256ac7bd5"


def migrate() -> None:
    """Apply all pending Alembic migrations."""
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_config, "head")


def verify() -> None:
    """Verify required tables and Alembic revision."""
    inspector = inspect(engine)

    missing_tables = {
        table
        for table in EXPECTED_TABLES
        if not inspector.has_table(table)
    }

    if missing_tables:
        raise RuntimeError(
            "Missing required tables: "
            + ", ".join(sorted(missing_tables))
        )

    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()

    if revision != EXPECTED_REVISION:
        raise RuntimeError(
            f"Unexpected Alembic revision: {revision!r}. "
            f"Expected {EXPECTED_REVISION!r}."
        )

    print("Database migration and verification passed.")
    print("Required table: user_sessions")
    print(f"Alembic revision: {revision}")


def main() -> int:
    try:
        print("Running Session Service database migrations...")
        migrate()

        print("Verifying Session Service database...")
        verify()

        return 0

    except Exception as exc:
        print(f"ERROR: Database migration/verification failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
    