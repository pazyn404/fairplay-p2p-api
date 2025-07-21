from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session
from repositories import game_repositories
from decorators import format_response
from formatters import format_errors


@app.api_route("/games/{game_name}", methods=["GET"])
@format_response
async def available_games(game_name: str, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    postgres_session.set(session)

    if game_name not in game_repositories:
        return format_errors(["Game does not exist"], 400)

    game_repository = game_repositories[game_name]()
    games = await game_repository.get_all_active_games()
    for game in games:
        await game_repository.fetch_related(game)

    return {"games": [game.data for game in games]}, 200
