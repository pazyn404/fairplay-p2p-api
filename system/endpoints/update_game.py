from time import time

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session, entity_cache
from entities import Host
from repositories import UserRepository, game_repositories
from decorators import format_response
from formatters import (
    format_payload,
    format_errors,
    format_verification_errors
)
from payload_structures import update_game_structures


@app.api_route("/games/{game_name}", methods=["PUT", "PATCH"])
@format_response
async def update_game(game_name: str, request: Request, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    entity_cache.set({})
    postgres_session.set(session)

    if game_name not in game_repositories:
        return format_errors(["Game does not exist"], 400)

    payload = await request.json()
    update_game_structure = update_game_structures[game_name]
    formatted_payload, errors = format_payload(payload, update_game_structure)
    if errors:
        return format_errors(errors, 400)

    user_repository = UserRepository()
    game_repository = game_repositories[game_name]()

    game = await game_repository.get_by_id(formatted_payload["id"], for_update=True)
    if not game:
        return format_errors(["Game not found"], 404)

    user = await user_repository.get_by_id(game.user_id, for_update=True)

    _time = int(time())
    await game_repository.fetch_related(game)
    game.store_prev_data()
    game.update(updated_at=_time, **formatted_payload)
    game.update_related()
    game.fill_from_related()

    errors = game.verify()
    if errors:
        return format_verification_errors(errors)

    await user_repository.save(user)
    await game_repository.save(game)
    await session.commit()

    return game.data, 200
