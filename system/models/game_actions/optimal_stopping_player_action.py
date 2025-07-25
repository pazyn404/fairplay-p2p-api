from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base_game_action import BaseGameActionModel


class OptimalStoppingPlayerActionModel(BaseGameActionModel):
    __tablename__ = "optimal_stopping_player_actions"

    GAME_TABLE_NAME = "optimal_stopping_games"

    action: Mapped[str] = mapped_column(nullable=False)
