from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from mixins import VerifySignatureMixin
from .base_model import BaseModel
from ._abstract_mapping import mapping


class BaseGameAction(VerifySignatureMixin, BaseModel):
    __abstract__ = True

    DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id",
        "game_revision|{GAME_MODEL}:game_id.action_number","created_at", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id",
        "game_revision|{GAME_MODEL}:game_id.action_number", "created_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = [
        "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id",
        "game_revision|{GAME_MODEL}:game_id.action_number", "game_action_number|{GAME_MODEL}:game_id.actions_count"
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    action_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)

    def __init_subclass__(cls, **kwargs):
        game_model_table_name = mapping[cls.__name__]["game_id"]
        cls.game_id: Mapped[int] = mapped_column(ForeignKey(f"{game_model_table_name}.id"), nullable=False, index=True)

        super().__init_subclass__(**kwargs)