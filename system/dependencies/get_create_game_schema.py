from fastapi import HTTPException, Request, status

from schemas.request import BaseCreateGameRequestSchema, create_game_request_schemas


async def get_create_game_schema(request: Request, game_name: str) -> BaseCreateGameRequestSchema:
    if game_name not in create_game_request_schemas:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Game does not exist"])

    payload = await request.json()
    return create_game_request_schemas[game_name].model_validate(payload)
