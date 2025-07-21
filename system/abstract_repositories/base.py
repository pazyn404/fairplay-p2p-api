import inspect
from abc import abstractmethod

from entities import BaseEntity
from exceptions import ViolatedConstraintError


class AbstractBaseRepository:
    @abstractmethod
    async def save(self, entity: BaseEntity) -> None:
        raise NotImplementedError

    async def violated_constraints(self, entity: BaseEntity) -> list[str]:
        errors = []
        for name, f in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if name.startswith("violated_constraint_"):
                try:
                    await f(self, entity)
                except ViolatedConstraintError as e:
                    errors.append(e)

        return errors
