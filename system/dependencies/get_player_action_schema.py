from fastapi import HTTPException, Request, status

from schemas.p2p import BaseGamePlayerActionRequestSchema, game_player_action_request_schemas


async def get_player_action_schema(request: Request, game_name: str) -> BaseGamePlayerActionRequestSchema:
    if game_name not in game_player_action_request_schemas:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=["Game does not exist"])

    payload = await request.json()
    return game_player_action_request_schemas[game_name].model_validate(payload)
