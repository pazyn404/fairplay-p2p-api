from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

import views
import middlewares
import exception_handlers
