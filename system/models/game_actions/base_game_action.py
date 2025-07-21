from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..base import BaseModel


class BaseGameActionModel(BaseModel):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action_number: Mapped[int] = mapped_column(nullable=False)
    game_action_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.game_id: Mapped[int] = mapped_column(ForeignKey(f"{cls.GAME_TABLE_NAME}.id"), nullable=False, index=True)
