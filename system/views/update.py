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
from payload_structures import update_structures


models = {
    "host": Host,
    **game_models
}


@app.api_route("/{plural_model_name}", methods=["PUT", "PATCH"])
@format_response
async def update(plural_model_name: str, request: Request, session: AsyncSession = Depends(get_session)):
    model_name = inflect_engine.singular_noun(plural_model_name)
    model = models.get(model_name)
    if not model:
        return format_errors(["Model does not exist"], 400)

    payload = await request.json()
    structure = update_structures[model_name]
    formatted_payload, errors = format_payload(payload, structure)
    if errors:
        return format_errors(errors, 400)

    query = select(model).with_for_update().filter_by(id=formatted_payload["id"])
    res = await session.execute(query)
    instance = res.scalar()
    if not instance:
        return format_errors(["Instance not found"], 404)

    query = select(User).with_for_update().filter_by(id=instance.user_id)
    res = await session.execute(query)
    user = res.scalar()

    await instance.fetch_related(session)

    prev_data = instance.__dict__.copy()
    instance.update(**formatted_payload, action_number=user.action_number + 1, updated_at=int(time()))
    instance.update_related(prev_data)

    errors = await instance.violated_constraints(session)
    if errors:
        return format_errors(errors, 409)

    errors, status_code = instance.verify(prev_data)
    if errors:
        await session.rollback()
        return format_errors(errors, status_code)

    await session.commit()

    return instance.data, 200
