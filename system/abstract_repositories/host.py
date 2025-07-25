from abc import abstractmethod

from entities import Host
from .base import AbstractBaseRepository


class AbstractHostRepository(AbstractBaseRepository):
    @abstractmethod
    async def get_by_id(self, id: int, for_update: bool) -> Host:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int, for_update: bool) -> Host:
        raise NotImplementedError

    @abstractmethod
    async def fetch_related(self, host: Host) -> None:
        raise NotImplementedError

    @abstractmethod
    async def violated_constraint_unique_host(self, host: Host) -> None:
        raise NotImplementedError

    @abstractmethod
    async def violated_constraint_unique_domain(self, host: Host) -> None:
        raise NotImplementedError
