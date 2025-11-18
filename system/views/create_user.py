from time import time

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session
from entities import User
from repositories import UserRepository
from dependencies import get_session
from schemas.request import CreateUserRequestSchema
from schemas.response import UserResponseSchema, ErrorResponseSchema


@app.api_route(
    "/users",
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorResponseSchema}
    },
    response_model=UserResponseSchema,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    methods=["POST"]
)
async def create_user(payload: CreateUserRequestSchema, session: AsyncSession = Depends(get_session)):
    postgres_session.set(session)

    user_repository = UserRepository()

    _time = int(time())
    user = User(created_at=_time, **payload.model_dump())

    user.verify()

    await user_repository.save(user)
    await session.commit()

    return UserResponseSchema.model_validate(user)
