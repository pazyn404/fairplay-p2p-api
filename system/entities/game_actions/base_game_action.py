from mixins import VerifyUserSignatureMixin
from ..base import BaseEntity


class BaseGameAction(VerifyUserSignatureMixin, BaseEntity):
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

    @property
    def user_signature_data(self) -> dict[str, int | str]:
        return {
            "user_id": self.user_id,
            "action_number": self.action_number,
            "game_name": self.game.__class__.GAME_NAME,
            "game_id": self.game_id,
            "game_revision": self.game.action_number,
            "game_action_number": self.game_action_number
        }

    @property
    def system_signature_data(self) -> dict[str, int | str]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_number": self.action_number,
            "game_name": self.game.__class__.GAME_NAME,
            "game_id": self.game_id,
            "game_revision": self.game.action_number,
            "game_action_number": self.game_action_number,
            "created_at": self.created_at
        }

    def fill_from_related(self) -> None:
        self.action_number = self.user.action_number
        self.game_action_number = self.game.game_action_number
