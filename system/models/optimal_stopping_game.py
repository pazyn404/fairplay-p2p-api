from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
import numpy as np

from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    __mapper_args__ = {
        "polymorphic_identity": "optimal_stopping_game",
        "polymorphic_load": "selectin"
    }

    GAME_NAME = "optimal stopping"

    DATA_ATTRIBUTES = BaseGame.DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGame.SYSTEM_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    USER_SIGNATURE_ATTRIBUTES = BaseGame.USER_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    id: Mapped[int] = mapped_column(ForeignKey("base_game.id"), primary_key=True)
    numbers_count: Mapped[int] = mapped_column(nullable=False)
    mean: Mapped[int] = mapped_column(nullable=False)
    std: Mapped[int] = mapped_column(nullable=False)
    top: Mapped[int] = mapped_column(nullable=False)

    def player_win(self):
        rng = np.random.default_rng(int.from_bytes(self.seed))
        numbers = rng.normal(loc=self.mean, scale=self.std, size=self.numbers_count).astype(int).tolist()

        for i, host_action in enumerate(self.host_actions):
            if host_action.number != numbers[i]:
                self.winner_id = self.player_id
                return

        numbers.sort(key=lambda x: -x)
        return numbers[self.top - 1] <= self.host_actions[-1].number
