from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    url = settings.database_url
    connect_args = {}
    if url.startswith("sqlite"):
        # SQLite needs this for usage in threaded FastAPI contexts.
        connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
