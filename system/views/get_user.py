from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session
from repositories import UserRepository
from dependencies import get_session
from schemas.response import UserResponseSchema, ErrorResponseSchema


@app.api_route(
    "/users/{id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema}
    },
    response_model=UserResponseSchema,
    response_model_by_alias=False,
    methods=["GET"]
)
async def get_user(id: int, session: AsyncSession = Depends(get_session)):
    postgres_session.set(session)

    user_repository = UserRepository()
    user = await user_repository.get_by_id(id, for_update=False)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["User not found"])

    return UserResponseSchema.model_validate(user)
