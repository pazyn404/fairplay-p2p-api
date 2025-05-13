from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from config import inflect_engine
from models import Host, game_models
from decorators import format_response
from formatters import format_errors


@app.api_route("/{plural_game_model_name}", methods=["GET"])
@format_response
async def available_games(plural_game_model_name: str, session: AsyncSession = Depends(get_session)):
    game_model_name = inflect_engine.singular_noun(plural_game_model_name)
    game_model = game_models.get(game_model_name)
    if not game_model:
        return format_errors(["Model does not exist"], 400)

    query = select(game_model).join(Host, game_model.user_id == Host.user_id).filter(
        game_model.active == True, game_model.player_id.is_(None)
    )
    res = await session.execute(query)
    games = res.scalars().all()

    return {"games": [await game.part_data for game in games]}, 200
