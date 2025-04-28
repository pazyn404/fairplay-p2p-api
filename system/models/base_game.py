from abc import abstractmethod
from hashlib import sha256

from app import db
from config import VerificationError
from mixins import VerifySignatureMixin
from .base_model import BaseModel


class BaseGame(VerifySignatureMixin, BaseModel):
    __abstract__ = True

    PART_DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "bet", "duration", "seed_hash", "created_at", "updated_at","system_signature"
    ]
    DATA_ATTRIBUTES = [
        "id", "user_id", "player_id", "winner_id", "action_number", "actions_count", "game_name|GAME_NAME", "bet", "duration",
        "active", "seed_hash", "seed", "started_at", "finished_at", "created_at", "updated_at",
        "player_actions|[]{PLAYER_ACTION_MODEL}:game_id:id.data", "host_actions|[]{HOST_ACTION_MODEL}:game_id:id.data", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "player_id", "winner_id", "action_number", "actions_count", "game_name|GAME_NAME", "bet", "duration",
        "active", "seed_hash", "seed", "started_at", "finished_at", "created_at", "updated_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "game_name|GAME_NAME", "bet", "duration", "active", "seed_hash", "seed"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    player_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    winner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)
    action_number = db.Column(db.Integer, nullable=False)
    actions_count = db.Column(db.Integer, nullable=False, default=0)
    bet = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    seed_hash = db.Column(db.LargeBinary, nullable=False)
    seed = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.Integer, nullable=True)
    finished_at = db.Column(db.Integer, nullable=True)
    user_signature = db.Column(db.LargeBinary, nullable=False)
    paid_out = db.Column(db.Boolean, nullable=False, default=False)

    @abstractmethod
    def player_win(self):
        raise NotImplementedError

    @property
    def part_data(self):
        return self._parse_attrs(self.__class__.PART_DATA_ATTRIBUTES)

    def complete(self):
        if self.player_win():
            self.winner_id = self.player_id
        else:
            self.winner_id = self.user_id

    def verify_seed_hash(self):
        if self.seed is None:
            return

        if sha256(self.seed).digest() != self.seed_hash:
            raise VerificationError("Seed hash does not match", 409)

    def verify_host_exist(self):
        from .host import Host

        host = db.session.query(Host).filter_by(user_id=self.user_id).first()
        if not host:
            raise VerificationError("Host is not set up", 409)

    def verify_host_active(self):
        from .host import Host

        host = db.session.query(Host).filter_by(user_id=self.user_id).first()
        if not host:
            return

        if not host.active and self.active:
            raise VerificationError("Host is not active", 409)

    def verify_pending(self):
        if self.winner_id is not None:
            raise VerificationError("Game is already complete", 409)
        if self.player_id is not None:
            raise VerificationError("Game has been started", 409)

    def verify_user_balance(self, prev_bet, prev_active):
        from .user import User

        user = db.session.get(User, self.user_id)
        if self.active:
            if prev_active:
                if user.balance < self.bet - prev_bet:
                    raise VerificationError("Insufficient balance", 409)
            else:
                if user.balance < self.bet:
                    raise VerificationError("Insufficient balance", 409)

    def update_related_user_balance(self, prev_bet, prev_active):
        from .user import User

        user = db.session.get(User, self.user_id)
        if self.active:
            if prev_active:
                user.balance -= self.bet - prev_bet
            else:
                user.balance -= self.bet
        else:
            if prev_active:
                user.balance += prev_bet
