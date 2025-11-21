import json
from time import time
from typing import Union

import httpx
from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session, entity_cache
from logger import logger
from entities import game_host_action_entities, game_player_action_entities
from repositories import (
    UserRepository,
    HostRepository,
    game_repositories,
    game_host_action_repositories,
    game_player_action_repositories
)
from exceptions import VerificationError, VerificationErrorsList
from dependencies import get_session, get_player_action_schema
from schemas.response import game_response_schemas, ErrorResponseSchema
from schemas.p2p import (
    BaseGamePlayerActionRequestSchema,
    HostRevealSetupResponseSchema,
    game_player_action_for_host_request_schemas,
    game_host_action_response_schemas,
    game_host_action_for_player_response_schemas
)
from celery_app_tasks import complete_game_on_timeout, payout


HOST_ENDPOINT = "http://{domain}/{path}"


@app.api_route(
    "/play/{game_name}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorResponseSchema}
    },
    response_model=Union[*game_response_schemas.values()] | Union[*game_host_action_for_player_response_schemas.values()],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
    methods=["POST"]
)
async def play(
        game_name: str,
        player_payload: BaseGamePlayerActionRequestSchema = Depends(get_player_action_schema),
        session: AsyncSession = Depends(get_session)
):
    # player part
    entity_cache.set({})
    postgres_session.set(session)

    user_repository = UserRepository()
    host_repository = HostRepository()
    game_repository = game_repositories[game_name]()
    host_action_repository = game_host_action_repositories[game_name]()
    player_action_repository = game_player_action_repositories[game_name]()

    host_action_entity = game_host_action_entities[game_name]
    player_action_entity = game_player_action_entities[game_name]

    game_response_schema = game_response_schemas[game_name]
    game_player_action_for_host_request_schema = game_player_action_for_host_request_schemas[game_name]
    game_host_action_response_schema = game_host_action_response_schemas[game_name]
    game_host_action_for_player_response_schema = game_host_action_for_player_response_schemas[game_name]

    # player part
    player = await user_repository.get_by_id(player_payload.user_id, for_update=True)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["User not found"])
    game = await game_repository.get_by_id(player_payload.game_id, for_update=True)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Game not found"])

    player_action = player_action_entity(created_at=int(time()), **player_payload.model_dump())
    await player_action_repository.fetch_related(player_action)
    player_action.update_related()
    player_action.fill_from_related()

    player_action.verify()

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

    async with httpx.AsyncClient() as client:
        try:
            host = await host_repository.get_by_user_id(game.user_id, for_update=False)
            for_host_data = game_player_action_for_host_request_schema.model_validate(player_action)
            endpoint = HOST_ENDPOINT.format(domain=host.domain, path=f"play/{game_name}")
            host_request = await client.post(endpoint, json=for_host_data.model_dump())
        except httpx.RequestError as e:
            await force_game_complete([str(e)])
            return game_response_schema.model_validate(game)

    try:
        raw_host_payload = host_request.json()
    except json.decoder.JSONDecodeError as e:
        await force_game_complete([str(e)])
        return game_response_schema.model_validate(game)

    if player_action.is_last_action():
        try:
            host_payload = HostRevealSetupResponseSchema.model_validate(raw_host_payload)
        except ValidationError as e:
            await force_game_complete(e, host_payload=raw_host_payload)
            return game_response_schema.model_validate(game)

        game.update(**host_payload.model_dump())
        await game_repository.fetch_related(game)
        try:
            game.verify_user_signature()
        except VerificationError as e:
            await force_game_complete([str(e)], host_payload=raw_host_payload)
            return game_response_schema.model_validate(game)

        game.complete()

        payout.delay(game_name, game.id)

        await game_repository.save(game)
        await session.commit()

        return game_response_schema.model_validate(game)
    else:
        if player_action.is_first_action():
            complete_game_on_timeout.apply_async(args=[game_name, game.id], countdown=game.duration)

        try:
            host_payload = game_host_action_response_schema.model_validate(raw_host_payload)
        except ValidationError as e:
            await force_game_complete(e, host_payload=raw_host_payload)
            return game_response_schema.model_validate(game)

        host_action = host_action_entity(
            created_at=int(time()), user_id=game.user_id, game_id=game.id, **host_payload.model_dump()
        )
        await host_action_repository.fetch_related(host_action)

        host_action.update_related()
        host_action.fill_from_related()

        try:
            host_action.verify()
        except VerificationErrorsList as e:
            await force_game_complete(e, host_payload=host_payload)
            return game_response_schema.model_validate(game)

        await game_repository.save(game)
        await host_action_repository.save(host_action)
        await session.commit()

        return game_host_action_for_player_response_schema.model_validate(host_action)
