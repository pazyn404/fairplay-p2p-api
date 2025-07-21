import numpy as np

from app import db
from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    GAME_NAME = "optimal stopping"
    GAME_SYSTEM_ACTION_MODEL_NAME = "OptimalStoppingSystemAction"

    DATA_ATTRIBUTES = BaseGame.DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGame.SYSTEM_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    REVEALED_SIGNATURE_ATTRIBUTES = BaseGame.REVEALED_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    numbers_count = db.Column(db.Integer, nullable=False)
    mean = db.Column(db.Integer, nullable=False)
    std = db.Column(db.Integer, nullable=False)
    top = db.Column(db.Integer, nullable=False)

    def host_user_win(self) -> bool:
        rng = np.random.default_rng(int.from_bytes(self.seed))
        numbers = rng.normal(loc=self.mean, scale=self.std, size=self.numbers_count).astype(int).tolist()

        return sorted(numbers, reverse=True)[self.top - 1] > numbers[self.game_action_number - 2]
