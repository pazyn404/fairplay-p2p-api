from os import environ

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine(environ["DATABASE_URI"], isolation_level="REPEATABLE READ")
session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)
