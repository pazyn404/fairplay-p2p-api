from sqlalchemy.orm import Mapped, mapped_column

from .base_game_action import BaseGameActionModel


class OptimalStoppingHostActionModel(BaseGameActionModel):
    __tablename__ = "optimal_stopping_host_actions"

    GAME_TABLE_NAME = "optimal_stopping_games"

    number: Mapped[int] = mapped_column(nullable=False)
