import numpy as np

from exceptions import VerificationError
from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    GAME_NAME = "optimal stopping"

    def __init__(self, *, numbers_count: int, mean: int, std: int, top: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.numbers_count = numbers_count
        self.mean = mean
        self.std = std
        self.top = top

    @property
    def user_signature_data(self) -> dict[str, int | str | None]:
        return {
            **super().user_signature_data,
            "numbers_count": self.numbers_count,
            "mean": self.mean,
            "std": self.std,
            "top": self.top
        }

    @property
    def system_signature_data(self) -> dict[str, int | str | None]:
        return {
            **super().system_signature_data,
            "numbers_count": self.numbers_count,
            "mean": self.mean,
            "std": self.std,
            "top": self.top
        }

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
