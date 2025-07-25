from utils import sign
from .base_game_action import BaseGameAction


class BaseGameHostAction(BaseGameAction):
    FOR_PLAYER_DATA_ATTRIBUTES = [
        "action_number|player.action_number", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at",
        "system_signature|for_player_signature"
    ]
    FOR_PLAYER_SIGNATURE_ATTRIBUTES = [
        "action_number|player.action_number", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.game = None
        self.user = None
        self.player = None

    @property
    def for_player_data(self) -> dict:
        return self._parse_attrs(self.__class__.FOR_PLAYER_DATA_ATTRIBUTES)

    @property
    def for_player_signature_data(self) -> dict:
        return self._parse_attrs(self.__class__.FOR_PLAYER_SIGNATURE_ATTRIBUTES)

    @property
    def for_player_signature(self) -> bytes:
        data = self.for_player_signature_data
        signature = sign(data)

        return signature
