import json
from time import time

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session, entity_cache
from config import logger, HOST_ENDPOINT
from entities import game_host_action_entities, game_player_action_entities
from repositories import (
    UserRepository,
    HostRepository,
    game_repositories,
    game_host_action_repositories,
    game_player_action_repositories
)
from exceptions import VerificationError
from decorators import format_response
from formatters import (
    format_data,
    format_payload,
    format_errors,
    format_verification_errors
)
from payload_structures import (
    reveal_setup_structure,
    game_host_action_structures,
    game_player_action_structures
)


@app.api_route("/play/{game_name}", methods=["POST"])
@format_response
async def play(game_name: str, request: Request, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    from tasks.payout import payout
    from tasks.complete_game_on_timeout import complete_game_on_timeout
    # player part
    entity_cache.set({})
    postgres_session.set(session)

    if game_name not in game_repositories:
        return format_errors(["Game does not exist"], 400)

    user_repository = UserRepository()
    host_repository = HostRepository()
    game_repository = game_repositories[game_name]()
    host_action_repository = game_host_action_repositories[game_name]()
    player_action_repository = game_player_action_repositories[game_name]()

    host_action_entity = game_host_action_entities[game_name]
    player_action_entity = game_player_action_entities[game_name]

    host_action_structure = game_host_action_structures[game_name]
    player_action_structure = game_player_action_structures[game_name]

    # player part
    player_payload = await request.json()
    formatted_player_payload, errors = format_payload(player_payload, player_action_structure)
    if errors:
        return format_errors(errors, 400)

    player = await user_repository.get_by_id(formatted_player_payload["user_id"], for_update=True)
    if not player:
        return format_errors(["User not found"], 404)
    game = await game_repository.get_by_id(formatted_player_payload["game_id"], for_update=True)
    if not game:
        return format_errors(["Game not found"], 404)

    player_action = player_action_entity(created_at=int(time()), **formatted_player_payload)
    await player_action_repository.fetch_related(player_action)
    player_action.update_related()
    player_action.fill_from_related()

    errors = player_action.verify()
    if errors:
        return format_verification_errors(errors)

    await user_repository.save(player)
    await player_action_repository.save(player_action)
    # host part
    async def force_game_complete(errors, *, host_payload=None):
        logger.critical(errors, extra={"player_payload": player_payload, "host_payload": host_payload})

        game.winner_id = player_action.user_id
        payout.delay(game_name, game.id)

        await game_repository.fetch_related(game)
        await game_repository.save(game)
        await session.commit()

    host = await host_repository.get_by_user_id(game.user_id, for_update=False)

    for_host_data = player_action.for_host_data
    formatted_for_host_data = format_data(for_host_data)
    async with httpx.AsyncClient() as client:
        try:
            endpoint = HOST_ENDPOINT.format(domain=host.domain, path=f"play/{game_name}")
            host_request = await client.post(endpoint, json=formatted_for_host_data)
        except httpx.RequestError as e:
            await force_game_complete([str(e)])
            return game.data, 200

    try:
        host_payload = host_request.json()
    except json.decoder.JSONDecodeError as e:
        await force_game_complete([str(e)])
        return game.data, 200

    if player_action.is_last_action():
        structure = reveal_setup_structure
        formatted_host_payload, errors = format_payload(host_payload, structure)
        if errors:
            await force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        game.update(**formatted_host_payload)
        await game_repository.fetch_related(game)
        try:
            game.verify_user_signature()
        except VerificationError as e:
            await force_game_complete([str(e)], host_payload=host_payload)
            return game.data, 200

        game.complete()

        payout.delay(game_name, game.id)

        await game_repository.save(game)
        await session.commit()

        return game.data, 200
    else:
        if player_action.is_first_action():
            complete_game_on_timeout.apply_async(args=[game_name, game.id], countdown=game.duration)

        formatted_host_payload, errors = format_payload(host_payload, host_action_structure)
        if errors:
            await force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        host_action = host_action_entity(
            created_at=int(time()), user_id=game.user_id, game_id=game.id, **formatted_host_payload
        )
        await host_action_repository.fetch_related(host_action)

        host_action.update_related()
        host_action.fill_from_related()

        errors = host_action.verify()
        if errors:
            await force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        await game_repository.save(game)
        await host_action_repository.save(host_action)
        await session.commit()

        return host_action.for_player_data, 200
