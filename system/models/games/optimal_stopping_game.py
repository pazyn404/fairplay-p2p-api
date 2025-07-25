from sqlalchemy.orm import Mapped, mapped_column

from .base_game import BaseGameModel


class OptimalStoppingGameModel(BaseGameModel):
    __tablename__ = "optimal_stopping_games"

    numbers_count: Mapped[int] = mapped_column(nullable=False)
    mean: Mapped[int] = mapped_column(nullable=False)
    std: Mapped[int] = mapped_column(nullable=False)
    top: Mapped[int] = mapped_column(nullable=False)
