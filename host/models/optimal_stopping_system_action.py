import numpy as np

from app import db
from config import VerificationError
from .base_game_system_action import BaseGameSystemAction


class OptimalStoppingSystemAction(BaseGameSystemAction):
    __mapper_args__ = {
        "polymorphic_identity": "optimal_stopping_system_action",
        "polymorphic_load": "selectin"
    }

    DATA_ATTRIBUTES = BaseGameSystemAction.DATA_ATTRIBUTES + ["action"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameSystemAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["action"]

    FOR_SYSTEM_DATA_ATTRIBUTES = BaseGameSystemAction.FOR_SYSTEM_DATA_ATTRIBUTES + ["number"]
    FOR_SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameSystemAction.FOR_SYSTEM_SIGNATURE_ATTRIBUTES + ["number"]

    action = db.Column(db.String(4), nullable=False)

    @property
    def number(self):
        rng = np.random.default_rng(int.from_bytes(self.game.seed))
        numbers = rng.normal(loc=self.game.mean, scale=self.game.std, size=self.game.numbers_count).astype(int).tolist()
        return numbers[self.game.actions_count - 1]

    def is_last_action(self):
        return self.action == "stop"

    def verify_next_allowed(self):
        if self.action != "next":
            return

        if self.game_action_number == self.game.numbers_count + 1:
            raise VerificationError("The last number has already been reached", 409)

    def verify_action_allowed(self):
        if self.action not in ("next", "stop"):
            raise VerificationError("Invalid action", 409)

    def verify_first_action(self):
        if self.game.actions_count == 1 and self.action == "stop":
            raise VerificationError("Invalid first action", 409)
