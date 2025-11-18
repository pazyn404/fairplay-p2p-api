from utils import sign
from .base_game_action import BaseGameAction


class BaseGameHostAction(BaseGameAction):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.game = None
        self.user = None
        self.player = None

    @property
    def for_player_system_signature_data(self) -> dict[str, int | str]:
        return {
            "action_number": self.player.action_number,
            "game_name": self.game.__class__.GAME_NAME,
            "game_revision": self.game.action_number,
            "game_action_number": self.game_action_number,
            "created_at": self.created_at
        }

    @property
    def for_player_system_signature(self) -> bytes:
        data = self.for_player_system_signature_data
        signature = sign(data)

        return signature
