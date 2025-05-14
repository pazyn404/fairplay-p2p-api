from utils import sign


class HostActionMixin:
    FOR_PLAYER_DATA_ATTRIBUTES = [
        "action_number|{GAME_MODEL}:game_id.User:player_id.action_number", "game_name|{GAME_MODEL}.GAME_NAME",
        "game_revision|{GAME_MODEL}:game_id.action_number", "created_at", "system_signature|for_player_signature"
    ]
    FOR_PLAYER_SIGNATURE_ATTRIBUTES = [
        "action_number|{GAME_MODEL}:game_id.User:player_id.action_number", "game_name|{GAME_MODEL}.GAME_NAME",
        "game_revision|{GAME_MODEL}:game_id.action_number", "created_at"
    ]

    @property
    async def for_player_data(self):
        return await self._parse_attrs(self.__class__.FOR_PLAYER_DATA_ATTRIBUTES)

    @property
    async def for_player_signature_data(self):
        return await self._parse_attrs(self.__class__.FOR_PLAYER_SIGNATURE_ATTRIBUTES)

    @property
    async def for_player_signature(self):
        data = await self.for_player_signature_data
        signature = sign(data)

        return signature
