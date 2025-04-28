import inspect
from abc import abstractmethod

from app import db
from config import VerificationError
from mixins import VerifyTimestampMixin
from utils import sign
from .base_model import BaseModel
from ._abstract_mapping import mapping


class BaseGameAction(VerifyTimestampMixin, BaseModel):
    __abstract__ = True

    DATA_ATTRIBUTES = [
        "id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id", "game_revision|{GAME_MODEL}:game_id.action_number",
        "game_action_number|{GAME_MODEL}:game_id.actions_count", "created_at", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "action_number", "game_id", "game_name|{GAME_MODEL}.GAME_NAME", "game_revision|{GAME_MODEL}:game_id.action_number",
        "game_action_number|{GAME_MODEL}:game_id.actions_count", "created_at"
    ]

    FOR_SYSTEM_DATA_ATTRIBUTES = ["user_signature|for_system_signature"]
    FOR_SYSTEM_SIGNATURE_ATTRIBUTES = [
        "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id", "game_revision|{GAME_MODEL}:game_id.action_number",
        "game_action_number|{GAME_MODEL}:game_id.actions_count"
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    action_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)

    def __init_subclass__(cls, **kwargs):
        game_model_table_name = mapping[cls.__name__]["game_id"]
        cls.game_id = db.Column(db.Integer, db.ForeignKey(f"{game_model_table_name}.id"), nullable=False, index=True)

    @abstractmethod
    def is_last_action(self):
        raise NotImplementedError

    def is_first_action(self):
        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)

        return game.actions_count == 1

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
        game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
        if game.started_at is not None and game.started_at + game.duration < self.created_at:
            raise VerificationError("Game is already complete", 409)

    def update_related(self, prev_data=None):
        prev_data = prev_data or {}
        prev_data = {f"prev_{param}": val for param, val in prev_data.items()}
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("update_related_"):
                params = list(inspect.signature(f).parameters)[1:]
                selected_prev_data = {param: prev_data.get(param) for param in params}
                f(self, **selected_prev_data)

    def update_related_game_started_time(self):
        if self.is_first_action():
            game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
            game.started_at = self.created_at

    def update_related_game_pending(self) -> None:
        if self.is_first_action():
            game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
            game.pending = True

    def update_related_game_complete(self):
        if self.is_last_action():
            game = db.session.get(self.__class__.GAME_MODEL, self.game_id)
            game.pending = False
            game.complete = True
