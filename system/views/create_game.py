from time import time
from typing import Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session, entity_cache
from entities import game_entities
from repositories import UserRepository, game_repositories
from dependencies import get_session, get_create_game_schema
from schemas.request import BaseCreateGameRequestSchema
from schemas.response import game_response_schemas, HostResponseSchema, ErrorResponseSchema
from schemas.response.games import OptimalStoppingGameResponseSchema


@app.api_route(
    "/games/{game_name}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorResponseSchema}
    },
    response_model=Union[*game_response_schemas.values()],
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    methods=["POST"]
)
async def create_game(
        game_name: str,
        payload: BaseCreateGameRequestSchema = Depends(get_create_game_schema),
        session: AsyncSession = Depends(get_session)
):
    entity_cache.set({})
    postgres_session.set(session)

    user_repository = UserRepository()
    game_repository = game_repositories[game_name]()

    user = await user_repository.get_by_id(payload.user_id, for_update=True)
    if not user:
        raise HTTPException(status_code=404, detail=["User not found"])

    _time = int(time())
    game = game_entities[game_name](created_at=_time, updated_at=_time, **payload.model_dump())
    await game_repository.fetch_related(game)
    game.update_related()
    game.fill_from_related()

    game.verify()

    await user_repository.save(user)
    await game_repository.save(game)
    await session.commit()

    game_response_schema = game_response_schemas[game_name]
    return game_response_schema.model_validate(game)
