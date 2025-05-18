from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from config import inflect_engine
from models import User, Host, game_models
from decorators import format_response
from formatters import format_errors


models = {
    "user": User,
    "host": Host,
    **game_models
}


@app.api_route("/{plural_model_name}/{instance_id}", methods=["GET"])
@format_response
async def get(plural_model_name: str, instance_id: int, session: AsyncSession = Depends(get_session)):
    model_name = inflect_engine.singular_noun(plural_model_name)
    model = models.get(model_name)
    if not model:
        return format_errors(["Model does not exist"], 400)

    instance = await session.get(model, instance_id)
    if not instance:
        return format_errors(["Instance not found"], 404)

    await instance.fetch_related(session)

    return instance.data, 200
