import json
from time import time

import httpx
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from config import logger, VerificationError, HOST_ENDPOINT
from models import User, Host, BaseGame, game_host_action_models, game_player_action_models
from decorators import format_response
from formatters import format_errors, format_payload, format_data
from payload_structures import reveal_setup_structure, game_host_action_structures, game_player_action_structures


@app.api_route("/play/{game_model_name}", methods=["POST"])
@format_response
async def play(game_model_name: str, request: Request, session: AsyncSession = Depends(get_session)):
    from tasks.payout import payout
    from tasks.complete_game_on_timeout import complete_game_on_timeout
    # player part
    if game_model_name not in game_player_action_structures:
        return format_errors(["Game does not exist"], 400)

    player_payload = await request.json()
    structure = game_player_action_structures[game_model_name]
    formatted_player_payload, errors = format_payload(player_payload, structure)
    if errors:
        return format_errors(errors, 400)

    query = select(User).with_for_update().filter_by(id=formatted_player_payload["user_id"])
    res = await session.execute(query)
    player = res.scalars().first()
    if not player:
        return format_errors(["User not found"], 404)

    query = select(BaseGame).with_for_update().filter_by(id=formatted_player_payload["game_id"])
    res = await session.execute(query)
    game = res.scalars().first()
    if not game:
        return format_errors(["Game not found"], 404)

    if game.player_id is None:
        game.player_id = player.id

    game_action_number = game.actions_count + 1

    player_action_model = game_player_action_models[game_model_name]
    player_action = player_action_model(
        **formatted_player_payload,
        action_number=player.action_number + 1,
        game_action_number=game_action_number,
        created_at=int(time())
    )

    session.add(player_action)
    await session.flush()

    await player_action.fetch_related(session)

    player_action_id = player_action.id
    player_action.id = None

    player_action.update_related()
    errors, status_code = player_action.verify()
    if errors:
        await session.rollback()
        return format_errors(errors, status_code)

    player_action.id = player_action_id
    await session.commit()
    # host part
    async def force_game_complete(errors, host_payload=None):
        logger.critical(errors, extra={"player_payload": player_payload, "host_payload": host_payload})

        game.winner_id = player.id
        payout.delay(game.id)

        await game.fetch_related(session)

        await session.commit()

    host_user = await session.get(User, game.user_id)
    query = select(Host).filter_by(user_id=game.user_id)
    res = await session.execute(query)
    host = res.scalars().first()

    for_host_data = player_action.for_host_data
    formatted_for_host_data = format_data(for_host_data)
    async with httpx.AsyncClient() as client:
        try:
            endpoint = HOST_ENDPOINT.format(domain=host.domain, path=f"play/{game_model_name}")
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
        try:
            game.verify_user_signature()
        except VerificationError as e:
            await force_game_complete([str(e)], host_payload=host_payload)
            return game.data, 200

        await game.fetch_related(session)
        game.complete()

        payout.delay(game.id)

        await session.commit()

        return game.data, 200
    else:
        if player_action.is_first_action():
            complete_game_on_timeout.apply_async(args=[game.id], countdown=game.duration)

        structure = game_host_action_structures[game_model_name]
        formatted_host_payload, errors = format_payload(host_payload, structure)
        if errors:
            await force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        host_action_model = game_host_action_models[game_model_name]
        host_action = host_action_model(
            **formatted_host_payload,
            game_id=game.id,
            user_id=host_user.id,
            action_number=host_user.action_number,
            game_action_number=game_action_number,
            created_at=int(time())
        )

        session.add(host_action)
        await session.flush()

        await host_action.fetch_related(session)

        host_action_id = host_action.id
        host_action.id = None

        errors, status_code = host_action.verify()
        if errors:
            await force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        host_action.id = host_action_id
        await session.commit()

        return host_action.for_player_data, 200
