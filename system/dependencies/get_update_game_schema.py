from fastapi import HTTPException, Request, status

from schemas.request import BaseUpdateGameRequestSchema, update_game_request_schemas


async def get_update_game_schema(request: Request, game_name: str) -> BaseUpdateGameRequestSchema:
    if game_name not in update_game_request_schemas:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Game does not exist"])

    payload = await request.json()
    return update_game_request_schemas[game_name].model_validate(payload)
