from os import environ
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


engine = create_engine(environ["DATABASE_URI"], isolation_level="REPEATABLE READ")
session_factory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session
