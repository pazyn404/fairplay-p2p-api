from time import time

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session
from entities import User
from repositories import UserRepository
from decorators import format_response
from formatters import (
    format_payload,
    format_errors,
    format_verification_errors
)
from payload_structures import create_user_structure


@app.api_route("/users", methods=["POST"])
@format_response
async def create_user(request: Request, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    postgres_session.set(session)

    payload = await request.json()
    formatted_payload, errors = format_payload(payload, create_user_structure)
    if errors:
        return format_errors(errors, 400)

    user_repository = UserRepository()

    _time = int(time())
    user = User(created_at=_time, **formatted_payload)
    errors = user.verify()
    if errors:
        return format_verification_errors(errors)

    await user_repository.save(user)
    await session.commit()

    return user.data, 201
