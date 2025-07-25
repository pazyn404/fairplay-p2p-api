from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session
from repositories import game_repositories
from decorators import format_response
from formatters import format_errors


@app.api_route("/games/{game_name}/{id}", methods=["GET"])
@format_response
async def get_game(game_name: str, id: int, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    postgres_session.set(session)

    if game_name not in game_repositories:
        return format_errors(["Game does not exist"], 400)

    game_repository = game_repositories[game_name]()
    game = await game_repository.get_by_id(id, for_update=False)
    if not game:
        return format_errors(["Game not found"], 404)

    await game_repository.fetch_related(game)

    return game.data, 200
