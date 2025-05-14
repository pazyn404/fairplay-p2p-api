from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
import numpy as np

from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    GAME_NAME = "optimal stopping"

    PART_DATA_ATTRIBUTES = BaseGame.PART_DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    DATA_ATTRIBUTES = BaseGame.DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGame.SYSTEM_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    USER_SIGNATURE_ATTRIBUTES = BaseGame.USER_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    numbers_count: Mapped[int] = mapped_column(nullable=False)
    mean: Mapped[int] = mapped_column(nullable=False)
    std: Mapped[int] = mapped_column(nullable=False)
    top: Mapped[int] = mapped_column(nullable=False)

    async def player_win(self):
        rng = np.random.default_rng(int.from_bytes(self.seed))
        numbers = rng.normal(loc=self.mean, scale=self.std, size=self.numbers_count).astype(int).tolist()

        query = (select(self.__class__.HOST_ACTION_MODEL).filter_by(game_id=self.id).
                        order_by(self.__class__.HOST_ACTION_MODEL.action_number))
        res = await self.session.execute(query)
        host_actions = res.scalars().all()
        for i, host_action in enumerate(host_actions):
            if host_action.number != numbers[i]:
                self.winner_id = self.player_id
                return

        numbers.sort(key=lambda x: -x)
        return numbers[self.top - 1] <= host_actions[-1].number
