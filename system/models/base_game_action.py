from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mixins import VerifySignatureMixin
from .base_model import BaseModel


class BaseGameAction(VerifySignatureMixin, BaseModel):
    __abstract__ = True

    DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number", "created_at", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = [
        "user_id", "action_number", "game_name|game.__class__.GAME_NAME", "game_id",
        "game_revision|game.action_number", "game_action_number"
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("base_game.id"), nullable=False, index=True)
    action_number: Mapped[int] = mapped_column(nullable=False)
    game_action_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)
