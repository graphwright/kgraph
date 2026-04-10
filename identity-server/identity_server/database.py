"""Database setup for the identity server using SQLModel."""

import os

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./identity.db")

engine = create_engine(DATABASE_URL)


def create_db_and_tables() -> None:
    """Create all database tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields an open SQLModel session."""
    with Session(engine) as session:
        yield session
