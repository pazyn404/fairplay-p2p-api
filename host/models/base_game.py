from hashlib import sha256

from app import db
from mixins import VerifyTimestampMixin
from utils import sign
from .base_model import BaseModel


class BaseGame(VerifyTimestampMixin, BaseModel):
    __mapper_args__ = {
        "polymorphic_on": "type"
    }

    DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "actions_count", "bet", "duration", "active", "seed", "created_at",
        "updated_at", "pending", "complete", "system_actions|system_actions.data", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", ("player_id", None), ("winner_id", None), "action_number", "actions_count", "game_name|GAME_NAME", "bet",
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
    actions_count = db.Column(db.Integer, nullable=False, default=0)
    bet = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    seed = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.Integer, nullable=True)
    pending = db.Column(db.Boolean, nullable=False, default=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)

    user = db.relationship("User", uselist=False)
    system_actions = db.relationship("BaseGameSystemAction", viewonly=True, uselist=True)

    @property
    def seed_hash(self):
        return sha256(self.seed).digest()

    @property
    def revealed_data(self):
        return self._parse_attrs(self.__class__.REVEALED_DATA_ATTRIBUTES)

    @property
    def revealed_signature_data(self):
        return self._parse_attrs(self.__class__.REVEALED_SIGNATURE_ATTRIBUTES)

    @property
    def revealed_signature(self):
        data = self.revealed_signature_data
        signature = sign(data)

        return signature
