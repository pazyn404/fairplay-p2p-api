from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from config import DBConfig


engine = create_async_engine(DBConfig.DATABASE_URI, isolation_level="REPEATABLE READ")
session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

sync_engine = create_engine(DBConfig.SYNC_DATABASE_URI, isolation_level="REPEATABLE READ")
sync_session_factory = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

def get_sync_session() -> Session:
    with sync_session_factory() as session:
        return session
