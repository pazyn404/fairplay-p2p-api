from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload, selectinload

from config import VerificationError
from mixins import VerifySignatureMixin, UpdateRelatedUserActionNumberMixin
from .base_model import BaseModel


class Host(VerifySignatureMixin, UpdateRelatedUserActionNumberMixin, BaseModel):
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

    user = relationship("User")
    existence_host = relationship(
        "Host",
        primaryjoin="and_(remote(Host.user_id) == foreign(Host.user_id), remote(Host.id) != foreign(Host.id))",
        viewonly=True,
        uselist=False
    )
    active_games = relationship(
        "BaseGame",
        primaryjoin="and_(BaseGame.user_id == foreign(Host.user_id), BaseGame.active == True)",
        viewonly=True,
        uselist=True
    )

    def _options(self):
        return [
            joinedload(Host.user),
            joinedload(Host.existence_host),
            selectinload(Host.active_games),
        ]

    def verify_turn_off(self):
        if not self.active and self.active_games:
            raise VerificationError("Host can't be turned off during active or pending games", 409)

    def verify_domain_change(self, prev_domain, prev_active):
        if not prev_domain or not self.active or not prev_active:
            return

        if self.domain != prev_domain:
            raise VerificationError("Host must be turned off to change domain", 409)

    def verify_unique(self):
        if self.existence_host:
            raise VerificationError("Host already exists", 409)
