from typing import Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session
from repositories import game_repositories
from dependencies import get_session
from schemas.response import game_response_schemas, ErrorResponseSchema


@app.api_route(
    "/games/{game_name}/{id}",
    response_model=Union[*game_response_schemas.values()],
    response_model_by_alias=False,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema}
    },
    methods=["GET"]
)
async def get_game(game_name: str, id: int, session: AsyncSession = Depends(get_session)):
    postgres_session.set(session)

    if game_name not in game_repositories:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Game does not exist"])

    game_repository = game_repositories[game_name]()
    game = await game_repository.get_by_id(id, for_update=False)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Game not found"])

    await game_repository.fetch_related(game)

    game_response_schema = game_response_schemas[game_name]
    return game_response_schema.model_validate(game)
