from abc import abstractmethod

from entities import User
from .base import AbstractBaseRepository


class AbstractUserRepository(AbstractBaseRepository):
    @abstractmethod
    async def get_by_id(self, id: int, for_update: bool) -> User:
        raise NotImplementedError
