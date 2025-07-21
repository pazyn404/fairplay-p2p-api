from abc import abstractmethod

from app import db
from mixins import (
    VerifySystemSignatureMixin
)
from exceptions import VerificationError
from utils import sign
from ..base import BaseModel


class BaseGameSystemAction(VerifySystemSignatureMixin,BaseModel):
    __abstract__ = True
    GAME_SYSTEM_ACTION_MODEL_NAME = "OptimalStoppingSystemAction"

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
    action_number = db.Column(db.Integer, nullable=False)
    game_action_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls.game_id = db.Column(db.Integer, db.ForeignKey(f"{cls.GAME_TABLE_NAME}.id"), nullable=False, index=True)

        cls.user = db.relationship("User", uselist=False)
        cls.game = db.relationship(cls.GAME_MODEL_NAME, uselist=False)

    @property
    def for_system_data(self) -> dict:
        return self._parse_attrs(self.__class__.FOR_SYSTEM_DATA_ATTRIBUTES)

    @property
    def for_system_signature_data(self) -> dict:
        return self._parse_attrs(self.__class__.FOR_SYSTEM_SIGNATURE_ATTRIBUTES)

    @property
    def for_system_signature(self) -> bytes:
        data = self.for_system_signature_data
        signature = sign(data)

        return signature

    @abstractmethod
    def is_last_action(self) -> bool:
        raise NotImplementedError

    def is_first_action(self) -> bool:
        return self.game.game_action_number == 1

    def fill_from_related(self) -> None:
        self.action_number = self.user.action_number
        self.game_action_number = self.game.game_action_number

    def verify_duration(self) -> None:
        if self.game.started_at is not None and self.game.started_at + self.game.duration < self.created_at:
            raise VerificationError("Game is already complete", 409)

    def update_related_game_game_action_number(self) -> None:
        self.game.game_action_number += 1

    def update_related_game_started_time(self) -> None:
        if self.is_first_action():
            self.game.started_at = self.created_at

    def update_related_game_pending(self) -> None:
        if self.is_first_action():
            self.game.pending = True

    def update_related_game_complete(self) -> None:
        if self.is_last_action():
            self.game.pending = False
            self.game.completed = True
