from exceptions import VerificationError
from .base_game_player_action import BaseGamePlayerAction


class OptimalStoppingPlayerAction(BaseGamePlayerAction):
    def __init__(self, *, action: str, **kwargs) -> None:
        super().__init__(**kwargs)

        self.action = action

    @property
    def user_signature_data(self) -> dict[str, int | str]:
        return {
            **super().user_signature_data,
            "action": self.action
        }

    @property
    def system_signature_data(self) -> dict[str, int | str]:
        return {
            **super().system_signature_data,
            "action": self.action
        }

    @property
    def for_host_system_signature_data(self) -> dict[str, int | str]:
        return {
            **super().for_host_system_signature_data,
            "action": self.action
        }

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
