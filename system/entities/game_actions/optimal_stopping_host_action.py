from .base_game_host_action import BaseGameHostAction


class OptimalStoppingHostAction(BaseGameHostAction):
    DATA_ATTRIBUTES = BaseGameHostAction.DATA_ATTRIBUTES + ["number"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameHostAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["number"]
    USER_SIGNATURE_ATTRIBUTES = BaseGameHostAction.USER_SIGNATURE_ATTRIBUTES + ["number"]

    FOR_PLAYER_DATA_ATTRIBUTES = BaseGameHostAction.FOR_PLAYER_DATA_ATTRIBUTES + ["number"]
    FOR_PLAYER_SIGNATURE_ATTRIBUTES = BaseGameHostAction.FOR_PLAYER_SIGNATURE_ATTRIBUTES + ["number"]

    def __init__(self, *, number: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.number = number
