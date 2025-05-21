from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_game_host_action import BaseGameHostAction


class OptimalStoppingHostAction(BaseGameHostAction):
    __mapper_args__ = {
        "polymorphic_identity": "optimal_stopping_host_action",
        "polymorphic_load": "selectin"
    }

    DATA_ATTRIBUTES = BaseGameHostAction.DATA_ATTRIBUTES + ["number"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameHostAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["number"]
    USER_SIGNATURE_ATTRIBUTES = BaseGameHostAction.USER_SIGNATURE_ATTRIBUTES + ["number"]

    FOR_PLAYER_DATA_ATTRIBUTES = BaseGameHostAction.FOR_PLAYER_DATA_ATTRIBUTES + ["number"]
    FOR_PLAYER_SIGNATURE_ATTRIBUTES = BaseGameHostAction.FOR_PLAYER_SIGNATURE_ATTRIBUTES + ["number"]

    id: Mapped[int] = mapped_column(ForeignKey("base_game_host_action.id"), primary_key=True)
    number: Mapped[int] = mapped_column(nullable=False)
