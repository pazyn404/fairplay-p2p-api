from app import db
from config import VerificationError
from mixins import PlayerActionMixin
from .base_game_action import BaseGameAction


class OptimalStoppingPlayerAction(PlayerActionMixin, BaseGameAction):
    DATA_ATTRIBUTES = BaseGameAction.DATA_ATTRIBUTES + ["action"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["action"]
    USER_SIGNATURE_ATTRIBUTES = BaseGameAction.USER_SIGNATURE_ATTRIBUTES + ["action"]

    FOR_HOST_DATA_ATTRIBUTES = PlayerActionMixin.FOR_HOST_DATA_ATTRIBUTES + ["action"]
    FOR_HOST_SIGNATURE_ATTRIBUTES = PlayerActionMixin.FOR_HOST_SIGNATURE_ATTRIBUTES + ["action"]

    action = db.Column(db.String(8), nullable=False)

    def is_last_action(self):
        return self.action == "stop"

    def verify_next_allowed(self):
        if self.action != "next":
            return

        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
        if game.numbers_count < game.actions_count:
            raise VerificationError("You have already reached the last number", 409)

    def verify_action_allowed(self):
        if self.action not in ("next", "stop"):
            raise VerificationError("Invalid action", 409)

    def verify_first_action(self):
        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
        if game.player_id is None and self.action == "stop":
            raise VerificationError("Invalid first action", 409)
