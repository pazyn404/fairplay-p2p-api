from sqlalchemy import select

from entities import User
from models import UserModel
from abstract_repositories import AbstractUserRepository
from decorators import entity_storage
from exceptions import ViolatedConstraintError
from context import postgres_session


class UserRepository(AbstractUserRepository):
    def __init__(self, *, primary: bool = True) -> None:
        self._session = postgres_session.get()

    async def save(self, user: User) -> None:
        if user.id is None:
            user_orm = UserModel(
                public_key=user.public_key,
                action_number=user.action_number,
                balance=user.balance,
                created_at=user.created_at
            )

            self._session.add(user_orm)
            await self._session.flush()

            user.id = user_orm.id
        else:
            user_orm = await self._session.get(UserModel, user.id)

            user_orm.update(
                action_number=user.action_number,
                balance=user.balance
            )

    @entity_storage
    async def get_by_id(self, id: int, *, for_update: bool = False) -> User | None:
        if for_update:
            query = select(UserModel).filter_by(id=id)
        else:
            query = select(UserModel).with_for_update().filter_by(id=id)

        res = await self._session.execute(query)
        user = res.scalar()
        if not user:
            return

        return User(
            id=user.id,
            public_key=user.public_key,
            action_number=user.action_number,
            balance=user.balance,
            created_at=user.created_at
        )
