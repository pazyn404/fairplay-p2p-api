from abc import abstractmethod

from entities import BaseGameAction
from .base import AbstractBaseRepository


class AbstractBaseGameActionRepository(AbstractBaseRepository):
    @abstractmethod
    async def get_by_game_id(self, game_id: int) -> list[BaseGameAction]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_related(self, game_action: BaseGameAction) -> None:
        raise NotImplementedError
