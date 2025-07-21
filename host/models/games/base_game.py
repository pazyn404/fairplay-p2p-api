from abc import abstractmethod
from hashlib import sha256

from app import db
from mixins import (
    VerifySystemSignatureMixin,
    UpdateRelatedUserActionNumberMixin
)
from utils import sign
from ..base import BaseModel


class BaseGame(VerifySystemSignatureMixin, UpdateRelatedUserActionNumberMixin, BaseModel):
    __abstract__ = True

    DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_action_number", "bet", "duration", "active", "seed", "win", "paid_out",
        "created_at", "updated_at", "pending", "completed", "system_actions|system_actions.data", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", ("player_id", None), ("winner_id", None), "action_number", "game_action_number", "game_name|GAME_NAME", "bet",
        "duration", "active", "seed_hash", ("seed", None), ("started_at", None), ("finished_at", None), "created_at", "updated_at"
    ]

    REVEALED_DATA_ATTRIBUTES = ["seed", "user_signature|revealed_signature"]
    REVEALED_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|__class__.GAME_NAME", "bet", "duration", "active", "seed_hash", "seed"
    ]

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    action_number = db.Column(db.Integer, nullable=False)
    game_action_number = db.Column(db.Integer, nullable=False, default=0)
    bet = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    seed = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.Integer, nullable=True)
    pending = db.Column(db.Boolean, nullable=False, default=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    win = db.Column(db.Boolean, nullable=True)
    paid_out = db.Column(db.Boolean, nullable=False, default=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls.user = db.relationship("User", uselist=False)
        cls.system_actions = db.relationship(cls.GAME_SYSTEM_ACTION_MODEL_NAME, viewonly=True, uselist=True)

    @property
    def seed_hash(self) -> bytes:
        return sha256(self.seed).digest()

    @property
    def revealed_data(self) -> dict[str, bytes]:
        return self._parse_attrs(self.__class__.REVEALED_DATA_ATTRIBUTES)

    @property
    def revealed_signature_data(self) -> dict[str, int | bool | str | bytes]:
        return self._parse_attrs(self.__class__.REVEALED_SIGNATURE_ATTRIBUTES)

    @property
    def revealed_signature(self) -> bytes:
        data = self.revealed_signature_data
        signature = sign(data)

        return signature

    @abstractmethod
    def host_user_win(self) -> bool:
        raise NotImplementedError

    def complete(self) -> None:
        self.win = self.host_user_win()

    def fill_from_related(self) -> None:
        self.action_number = self.user.action_number

    def update_related_user_balance(self, prev_bet: int | None, prev_active: int | None) -> None:
        if self.active:
            if prev_active:
                self.user.balance -= self.bet - prev_bet
            else:
                self.user.balance -= self.bet
        else:
            if prev_active:
                self.user.balance += prev_bet
