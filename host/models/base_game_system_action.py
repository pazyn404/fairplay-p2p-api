import inspect
from abc import abstractmethod

from app import db
from config import VerificationError
from mixins import VerifyTimestampMixin
from utils import sign
from .base_model import BaseModel


class BaseGameSystemAction(VerifyTimestampMixin, BaseModel):
    __mapper_args__ = {
        "polymorphic_on": "type"
    }

    DATA_ATTRIBUTES = [
        "id", "action_number", "game_name|game.__class__.GAME_NAME",
        "game_id", "game_revision|game.action_number",
        "game_action_number", "created_at", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "action_number", "game_id", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]

    FOR_SYSTEM_DATA_ATTRIBUTES = ["user_signature|for_system_signature"]
    FOR_SYSTEM_SIGNATURE_ATTRIBUTES = [
        "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number"
    ]

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    game_id = db.Column(db.Integer, db.ForeignKey("base_game.id"), nullable=False, index=True)
    action_number = db.Column(db.Integer, nullable=False)
    game_action_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)

    user = db.relationship("User", uselist=False)
    game = db.relationship("BaseGame", uselist=False)

    @abstractmethod
    def is_last_action(self):
        raise NotImplementedError

    def is_first_action(self):
        return self.game_action_number == 1

    @property
    def for_system_data(self):
        return self._parse_attrs(self.__class__.FOR_SYSTEM_DATA_ATTRIBUTES)

    @property
    def for_system_signature_data(self):
        return self._parse_attrs(self.__class__.FOR_SYSTEM_SIGNATURE_ATTRIBUTES)

    @property
    def for_system_signature(self):
        data = self.for_system_signature_data
        signature = sign(data)

        return signature

    def verify_duration(self):
        if self.game.started_at is not None and self.game.started_at + self.game.duration < self.created_at:
            raise VerificationError("Game is already complete", 409)

    def update_related_game_actions_count(self):
        self.game.actions_count += 1

    def update_related_game_started_time(self):
        if self.is_first_action():
            self.game.started_at = self.created_at

    def update_related_game_pending(self) -> None:
        if self.is_first_action():
            self.game.pending = True

    def update_related_game_complete(self):
        if self.is_last_action():
            self.game.pending = False
            self.game.complete = True
