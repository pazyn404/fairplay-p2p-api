from abc import abstractmethod
from hashlib import sha256

from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column

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

    id: Mapped[int] = mapped_column(primary_key=True)
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

    @abstractmethod
    async def player_win(self):
        raise NotImplementedError

    @property
    async def part_data(self):
        return await self._parse_attrs(self.__class__.PART_DATA_ATTRIBUTES)

    async def complete(self):
        if await self.player_win():
            self.winner_id = self.player_id
        else:
            self.winner_id = self.user_id

    async def verify_seed_hash(self):
        if self.seed is None:
            return

        if sha256(self.seed).digest() != self.seed_hash:
            raise VerificationError("Seed hash does not match", 409)

    async def verify_host_exist(self):
        from .host import Host

        query = select(Host).filter_by(user_id=self.user_id)
        res = await self.session.execute(query)
        host = res.scalars().first()
        if not host:
            raise VerificationError("Host is not set up", 409)

    async def verify_host_active(self):
        from .host import Host

        query = select(Host).filter_by(user_id=self.user_id)
        res = await self.session.execute(query)
        host = res.scalars().first()
        if not host:
            return

        if not host.active and self.active:
            raise VerificationError("Host is not active", 409)

    async def verify_pending(self):
        if self.winner_id is not None:
            raise VerificationError("Game is already complete", 409)
        if self.player_id is not None:
            raise VerificationError("Game has been started", 409)

    async def verify_user_balance(self, prev_bet, prev_active):
        from .user import User

        user = await self.session.get(User, self.user_id)
        if self.active:
            if prev_active:
                if user.balance < self.bet - prev_bet:
                    raise VerificationError("Insufficient balance", 409)
            else:
                if user.balance < self.bet:
                    raise VerificationError("Insufficient balance", 409)

    async def update_related_user_balance(self, prev_bet, prev_active):
        from .user import User

        user = await self.session.get(User, self.user_id)
        if self.active:
            if prev_active:
                user.balance -= self.bet - prev_bet
            else:
                user.balance -= self.bet
        else:
            if prev_active:
                user.balance += prev_bet
