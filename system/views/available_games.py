from typing import Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session
from repositories import game_repositories
from dependencies import get_session
from schemas.response import game_without_relations_response_schemas, ErrorResponseSchema


@app.api_route(
    "/games/{game_name}",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema}
    },
    response_model=list[Union[*game_without_relations_response_schemas.values()]],
    response_model_by_alias=False,
    methods=["GET"]
)
async def available_games(game_name: str, session: AsyncSession = Depends(get_session)):
    postgres_session.set(session)

    if game_name not in game_repositories:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Game does not exist"])

    game_repository = game_repositories[game_name]()
    games = await game_repository.get_all_active_games()

    game_without_relations_response_schema = game_without_relations_response_schemas[game_name]
    return [game_without_relations_response_schema.model_validate(game) for game in games]
