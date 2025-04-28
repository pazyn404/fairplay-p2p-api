import numpy as np

from app import db
from config import VerificationError
from .base_game_action import BaseGameAction


class OptimalStoppingSystemAction(BaseGameAction):
    DATA_ATTRIBUTES = BaseGameAction.DATA_ATTRIBUTES + ["action"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["action"]

    FOR_SYSTEM_DATA_ATTRIBUTES = BaseGameAction.FOR_SYSTEM_DATA_ATTRIBUTES + ["number"]
    FOR_SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameAction.FOR_SYSTEM_SIGNATURE_ATTRIBUTES + ["number"]

    action = db.Column(db.String(8), nullable=False)

    @property
    def number(self):
        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
        rng = np.random.default_rng(int.from_bytes(game.seed))
        numbers = rng.normal(loc=game.mean, scale=game.std, size=game.numbers_count).astype(int).tolist()
        return numbers[game.actions_count - 1]

    def is_last_action(self):
        return self.action == "stop"

    def verify_next_allowed(self):
        if self.action != "next":
            return

        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
        game_actions = db.session.query(OptimalStoppingSystemAction).filter_by(game_id=self.game_id).all()
        if len(game_actions) == game.numbers_count:
            raise VerificationError("Last number already reached", 409)

    def verify_action_allowed(self):
        if self.action not in ("next", "stop"):
            raise VerificationError("Invalid action", 409)

    def verify_first_action(self):
        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
        if game.actions_count == 1 and self.action == "stop":
            raise VerificationError("Invalid first action", 409)
