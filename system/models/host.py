from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload, selectinload

from config import VerificationError, ViolatedConstraintError
from mixins import VerifySignatureMixin, UpdateRelatedUserActionNumberMixin
from .base_model import BaseModel


class Host(VerifySignatureMixin, UpdateRelatedUserActionNumberMixin, BaseModel):
    DATA_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at"]
    USER_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active"]

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, unique=True, index=True)
    domain: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    active: Mapped[bool] = mapped_column(nullable=False)
    action_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    updated_at: Mapped[int] = mapped_column(nullable=False)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)

    user = relationship("User")
    active_games = relationship(
        "BaseGame",
        primaryjoin="and_(BaseGame.user_id == foreign(Host.user_id), BaseGame.active == True)",
        viewonly=True,
        uselist=True
    )

    def _options(self):
        return [
            joinedload(Host.user),
            selectinload(Host.active_games)
        ]

    async def violated_constraint_unique_host(self, session):
        if self.id is not None:
            return

        query = select(Host).filter_by(user_id=self.user_id)
        res = await session.execute(query)
        existence_host = res.scalars().first()
        if existence_host:
            raise ViolatedConstraintError("Host already exists")

    async def violated_constraint_unique_domain(self, session):
        query = select(Host).filter(Host.domain == self.domain, Host.user_id != self.user_id)
        res = await session.execute(query)
        existence_host = res.scalars().first()
        if existence_host:
            raise ViolatedConstraintError("Domain is already taken")

    def verify_turn_off(self):
        if not self.active and self.active_games:
            raise VerificationError("Host can't be turned off during active or pending games", 409)

    def verify_domain_change(self, prev_domain, prev_active):
        if not prev_domain or not self.active or not prev_active:
            return

        if self.domain != prev_domain:
            raise VerificationError("Host must be turned off to change domain", 409)
