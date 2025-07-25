from mixins import VerifySignatureMixin
from ..base import BaseEntity


class BaseGameAction(VerifySignatureMixin, BaseEntity):
    DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number", "created_at", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = [
        "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number"
    ]

    def __init__(
            self,
            *,
            id: int | None = None,
            user_id: int,
            game_id: int,
            action_number: int | None = None,
            game_action_number: int | None = None,
            created_at: int,
            user_signature: bytes
    ) -> None:
        super().__init__()

        self.id = id
        self.user_id = user_id
        self.game_id = game_id
        self.action_number = action_number
        self.game_action_number = game_action_number
        self.created_at = created_at
        self.user_signature = user_signature

    def fill_from_related(self) -> None:
        self.action_number = self.user.action_number
        self.game_action_number = self.game.game_action_number
