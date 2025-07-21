from exceptions import VerificationError
from .base_game_player_action import BaseGamePlayerAction


class OptimalStoppingPlayerAction(BaseGamePlayerAction):
    DATA_ATTRIBUTES = BaseGamePlayerAction.DATA_ATTRIBUTES + ["action"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGamePlayerAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["action"]
    USER_SIGNATURE_ATTRIBUTES = BaseGamePlayerAction.USER_SIGNATURE_ATTRIBUTES + ["action"]

    FOR_HOST_DATA_ATTRIBUTES = BaseGamePlayerAction.FOR_HOST_DATA_ATTRIBUTES + ["action"]
    FOR_HOST_SIGNATURE_ATTRIBUTES = BaseGamePlayerAction.FOR_HOST_SIGNATURE_ATTRIBUTES + ["action"]

    def __init__(self, *, action: str, **kwargs) -> None:
        super().__init__(**kwargs)

        self.action = action

    def is_last_action(self) -> bool:
        return self.action == "stop"

    def verify_next_allowed(self) -> None:
        if self.action != "next":
            return

        if self.game.numbers_count < self.game_action_number:
            raise VerificationError("The last number has already been reached", 409)

    def verify_action_allowed(self) -> None:
        if self.action not in ("next", "stop"):
            raise VerificationError("Invalid action", 409)

    def verify_first_action(self) -> None:
        if self.game_action_number == 1 and self.action == "stop":
            raise VerificationError("Invalid first action", 409)
