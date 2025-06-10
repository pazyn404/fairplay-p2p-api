from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config import VerificationError
from .base_game_player_action import BaseGamePlayerAction


class OptimalStoppingPlayerAction(BaseGamePlayerAction):
    __mapper_args__ = {
        "polymorphic_identity": "optimal_stopping_player_action",
        "polymorphic_load": "selectin"
    }

    DATA_ATTRIBUTES = BaseGamePlayerAction.DATA_ATTRIBUTES + ["action"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGamePlayerAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["action"]
    USER_SIGNATURE_ATTRIBUTES = BaseGamePlayerAction.USER_SIGNATURE_ATTRIBUTES + ["action"]

    FOR_HOST_DATA_ATTRIBUTES = BaseGamePlayerAction.FOR_HOST_DATA_ATTRIBUTES + ["action"]
    FOR_HOST_SIGNATURE_ATTRIBUTES = BaseGamePlayerAction.FOR_HOST_SIGNATURE_ATTRIBUTES + ["action"]

    id: Mapped[int] = mapped_column(ForeignKey("base_game_player_action.id"), primary_key=True)
    action: Mapped[str] = mapped_column(nullable=False)

    def is_last_action(self):
        return self.action == "stop"

    def verify_next_allowed(self):
        if self.action != "next":
            return

        if self.game.numbers_count < self.game_action_number:
            raise VerificationError("The last number has already been reached", 409)

    def verify_action_allowed(self):
        if self.action not in ("next", "stop"):
            raise VerificationError("Invalid action", 409)

    def verify_first_action(self):
        if self.game_action_number == 1 and self.action == "stop":
            raise VerificationError("Invalid first action", 409)
