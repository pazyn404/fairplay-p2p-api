import numpy as np

from exceptions import VerificationError
from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    GAME_NAME = "optimal stopping"

    DATA_ATTRIBUTES = BaseGame.DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGame.SYSTEM_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    USER_SIGNATURE_ATTRIBUTES = BaseGame.USER_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    def __init__(self, *, numbers_count: int, mean: int, std: int, top: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.numbers_count = numbers_count
        self.mean = mean
        self.std = std
        self.top = top

    def player_win(self) -> bool:
        rng = np.random.default_rng(int.from_bytes(self.seed))
        numbers = rng.normal(loc=self.mean, scale=self.std, size=self.numbers_count).astype(int).tolist()

        for i, host_action in enumerate(self.host_actions):
            if host_action.number != numbers[i]:
                self.winner_id = self.player_id
                return True

        numbers.sort(reverse=True)

        return numbers[self.top - 1] <= self.host_actions[-1].number

    def verify_top(self) -> None:
        if self.numbers_count <= self.top:
            raise VerificationError("Top must be smaller than numbers count", 409)
