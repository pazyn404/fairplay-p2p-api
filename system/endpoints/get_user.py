from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session
from repositories import UserRepository
from decorators import format_response
from formatters import format_errors



@app.api_route("/users/{id}", methods=["GET"])
@format_response
async def get_user(id: int, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    postgres_session.set(session)

    user_repository = UserRepository()
    user = await user_repository.get_by_id(id, for_update=False)
    if not user:
        return format_errors(["User not found"], 404)

    return user.data, 200
