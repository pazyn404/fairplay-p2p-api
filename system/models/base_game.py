from abc import abstractmethod
from hashlib import sha256

from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload, joinedload

from config import VerificationError
from mixins import VerifySignatureMixin, UpdateRelatedUserActionNumberMixin
from .base_model import BaseModel


class BaseGame(VerifySignatureMixin, UpdateRelatedUserActionNumberMixin, BaseModel):
    __mapper_args__ = {
        "polymorphic_abstract": True,
        "polymorphic_on": "type"
    }

    DATA_ATTRIBUTES = [
        "id", "user_id", "player_id", "winner_id", "action_number", "game_name|GAME_NAME", "bet", "duration",
        "active", "seed_hash", "seed", "started_at", "finished_at", "created_at", "updated_at",
        "player_actions|player_actions.data", "host_actions|host_actions.data", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "player_id", "winner_id", "action_number", "actions_count", "game_name|GAME_NAME", "bet",
        "duration", "active", "seed_hash", "seed", "started_at", "finished_at", "created_at", "updated_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|GAME_NAME", "bet", "duration", "active", "seed_hash", "seed"
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True, index=True)
    winner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True, index=True)
    action_number: Mapped[int] = mapped_column(nullable=False)
    actions_count: Mapped[int] = mapped_column(nullable=False, default=0)
    bet: Mapped[int] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False)
    seed_hash: Mapped[bytes] = mapped_column(nullable=False)
    seed: Mapped[bytes] = mapped_column(nullable=True)
    created_at: Mapped[int] = mapped_column(nullable=False)
    updated_at: Mapped[int] = mapped_column(nullable=False)
    started_at: Mapped[int] = mapped_column(nullable=True)
    finished_at: Mapped[int] = mapped_column(nullable=True)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)
    paid_out: Mapped[bool] = mapped_column(nullable=False, default=False)

    user = relationship(
        "User",
        primaryjoin="User.id == foreign(BaseGame.user_id)",
        uselist=False
    )
    host = relationship(
        "Host",
        primaryjoin="Host.user_id == foreign(BaseGame.user_id)",
        viewonly=True,
        uselist=False
    )

    player_actions = relationship(
        "BaseGamePlayerAction",
        order_by="BaseGamePlayerAction.game_action_number",
        viewonly=True,
        uselist=True
    )
    host_actions = relationship(
        "BaseGameHostAction",
        order_by="BaseGameHostAction.game_action_number",
        viewonly=True,
        uselist=True
    )

    @abstractmethod
    def player_win(self):
        raise NotImplementedError

    def _options(self):
        return [
            joinedload(self.__class__.user),
            joinedload(self.__class__.host),
            selectinload(self.__class__.player_actions),
            selectinload(self.__class__.host_actions)
        ]

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
        if not self.host:
            raise VerificationError("Host is not set up", 409)

    def verify_host_active(self):
        if not self.host:
            return

        if not self.host.active and self.active:
            raise VerificationError("Host is not active", 409)

    def verify_pending(self):
        if self.winner_id is not None:
            raise VerificationError("Game is already complete", 409)
        if self.player_id is not None:
            raise VerificationError("Game has been started", 409)

    def verify_user_balance(self):
        if self.user.balance < 0:
            raise VerificationError("Insufficient balance", 409)

    def update_related_user_balance(self, prev_bet, prev_active):
        if self.active:
            if prev_active:
                self.user.balance -= self.bet - prev_bet
            else:
                self.user.balance -= self.bet
        else:
            if prev_active:
                self.user.balance += prev_bet
