"""Database engine, session factory, and shared FastAPI dependency."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./taskflow.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a SQLAlchemy session and closes it after use.

    Reused across every endpoint so session logic is written once, not duplicated.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
