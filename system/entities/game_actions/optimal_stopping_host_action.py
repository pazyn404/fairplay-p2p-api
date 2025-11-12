from .base_game_host_action import BaseGameHostAction


class OptimalStoppingHostAction(BaseGameHostAction):
    def __init__(self, *, number: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.number = number

    @property
    def user_signature_data(self) -> dict[str, int | str]:
        return {
            **super().user_signature_data,
            "number": self.number
        }

    @property
    def system_signature_data(self) -> dict[str, int | str]:
        return {
            **super().system_signature_data,
            "number": self.number
        }

    @property
    def for_player_system_signature_data(self) -> dict[str, int | str]:
        return {
            **super().for_player_system_signature_data,
            "number": self.number
        }
