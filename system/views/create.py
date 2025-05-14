from time import time

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from config import inflect_engine
from models import User, Host, game_models
from decorators import format_response
from formatters import format_payload, format_errors
from payload_structures import create_structures


models = {
    "user": User,
    "host": Host,
    **game_models
}


@app.api_route("/{plural_model_name}", methods=["POST"])
@format_response
async def create(plural_model_name: str, request: Request, session: AsyncSession = Depends(get_session)):
    model_name = inflect_engine.singular_noun(plural_model_name)
    model = models.get(model_name)
    if not model:
        return format_errors(["Model does not exist"], 400)

    payload = await request.json()
    structure = create_structures[model_name]
    formatted_payload, errors = format_payload(payload, structure)
    if errors:
        return format_errors(errors, 400)

    _time = int(time())
    instance = model(created_at=_time, **formatted_payload)
    instance.session = session
    if model is not User:
        query = select(User).with_for_update().filter_by(id=formatted_payload["user_id"])
        res = await session.execute(query)
        user = res.scalars().first()
        if not user:
            return format_errors(["User not found"], 404)

        user.action_number += 1

        instance.action_number = user.action_number
        instance.updated_at = _time

    errors, status_code = await instance.verify()
    if errors:
        await session.rollback()
        return format_errors(errors, status_code)

    await instance.update_related()

    session.add(instance)
    await session.commit()

    return await instance.data, 201
