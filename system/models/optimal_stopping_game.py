import numpy as np

from app import db
from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    GAME_NAME = "optimal stopping"

    PART_DATA_ATTRIBUTES = BaseGame.PART_DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    DATA_ATTRIBUTES = BaseGame.DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGame.SYSTEM_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    USER_SIGNATURE_ATTRIBUTES = BaseGame.USER_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    numbers_count = db.Column(db.Integer, nullable=False)
    mean = db.Column(db.Integer, nullable=False)
    std = db.Column(db.Integer, nullable=False)
    top = db.Column(db.Integer, nullable=False)

    def player_win(self):
        rng = np.random.default_rng(int.from_bytes(self.seed))
        numbers = rng.normal(loc=self.mean, scale=self.std, size=self.numbers_count).astype(int).tolist()

        host_actions = (db.session.query(self.__class__.HOST_ACTION_MODEL).filter_by(game_id=self.id).
                        order_by(self.__class__.HOST_ACTION_MODEL.action_number).all())
        for i, host_action in enumerate(host_actions):
            if host_action.number != numbers[i]:
                self.winner_id = self.player_id
                return

        numbers.sort(key=lambda x: -x)
        return numbers[self.top - 1] <= host_actions[-1].number
