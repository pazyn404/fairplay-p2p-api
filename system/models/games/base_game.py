from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..base import BaseModel


class BaseGameModel(BaseModel):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    winner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action_number: Mapped[int] = mapped_column(nullable=False)
    game_action_number: Mapped[int] = mapped_column(nullable=False)
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
    paid_out: Mapped[bool] = mapped_column(nullable=False)
