from abc import abstractmethod

from entities import BaseGame
from .base import AbstractBaseRepository


class AbstractBaseGameRepository(AbstractBaseRepository):
    @abstractmethod
    async def get_by_id(self, id: int, for_update: bool) -> BaseGame:
        raise NotImplementedError

    @abstractmethod
    async def get_active_games(self, user_id: int) -> list[BaseGame]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_active_games(self) -> list[BaseGame]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_related(self, game: BaseGame) -> None:
        raise NotImplementedError
