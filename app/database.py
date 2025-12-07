from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema():
    """Create tables and repair a mismatched SQLite schema.

    When the dev SQLite database exists from an older revision, new columns
    (for example, recent billing period fields) are missing. SQLite will not
    add them automatically on ``create_all``; instead we drop and recreate the
    tables when we detect a mismatch. This keeps local runs from failing with
    ``OperationalError: table invoices has no column ...`` while avoiding
    destructive behavior on non-SQLite databases.
    """

    inspector = inspect(engine)
    # Only auto-recreate the schema for SQLite dev environments.
    if engine.url.get_backend_name() == "sqlite":
        existing_tables = inspector.get_table_names()
        if "invoices" in existing_tables:
            existing_columns = {col["name"] for col in inspector.get_columns("invoices")}
            expected_columns = set(Base.metadata.tables["invoices"].c.keys())
            if not expected_columns.issubset(existing_columns):
                Base.metadata.drop_all(bind=engine)
                Base.metadata.create_all(bind=engine)
                return

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
