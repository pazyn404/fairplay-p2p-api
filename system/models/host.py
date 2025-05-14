from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column

from config import VerificationError
from mixins import VerifySignatureMixin
from .base_model import BaseModel


class Host(VerifySignatureMixin, BaseModel):
    DATA_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at"]
    USER_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active"]

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(nullable=False)
    action_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    updated_at: Mapped[int] = mapped_column(nullable=False)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)

    async def verify_turn_off(self):
        from .base_game import BaseGame

        if self.active:
           return

        for game_model in BaseGame.__subclasses__():
            query = select(game_model).filter(
                game_model.user_id == self.user_id,
                game_model.active == True,
                game_model.winner_id.is_(None)
            )
            res = await self.session.execute(query)
            active_games = res.scalars().all()
            if active_games:
                raise VerificationError("Host can't be turned off during active or pending games", 409)

    async def verify_domain_change(self, prev_domain, prev_active):
        if not prev_domain or not self.active or not prev_active:
            return

        if self.domain != prev_domain:
            raise VerificationError("Host must be turned off to change domain", 409)

    async def verify_unique(self):
        query = select(Host).filter_by(user_id=self.user_id)
        res = await self.session.execute(query)
        host = res.scalars().first()
        if host and self.id != host.id:
            raise VerificationError("Host already exists", 409)
