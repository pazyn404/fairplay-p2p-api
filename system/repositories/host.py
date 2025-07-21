from sqlalchemy import select

from entities import Host
from models import HostModel
from abstract_repositories import AbstractHostRepository
from decorators import entity_storage
from exceptions import ViolatedConstraintError
from context import postgres_session


class HostRepository(AbstractHostRepository):
    def __init__(self, *, primary: bool = True) -> None:
        from .user import UserRepository
        from .games.base_game import BaseGameRepository

        self._session = postgres_session.get()
        if primary:
            self._user_repository = UserRepository(primary=False)
            self._game_repositories = [
                game_repository(primary=False)
                for game_repository in BaseGameRepository.__subclasses__()
            ]

    async def save(self, host: Host) -> None:
        if host.id is None:
            host_orm = HostModel(
                user_id=host.user_id,
                domain=host.domain,
                active=host.active,
                action_number=host.action_number,
                created_at=host.created_at,
                updated_at=host.updated_at,
                user_signature=host.user_signature
            )

            self._session.add(host_orm)
            await self._session.flush()

            host.id = host_orm.id
        else:
            host_orm = await self._session.get(HostModel, host.id)

            host_orm.update(
                domain=host.domain,
                active=host.active,
                action_number=host.action_number,
                updated_at=host.updated_at,
                user_signature=host.user_signature
            )

    @entity_storage
    async def get_by_id(self, id: int, *, for_update: bool = False) -> Host | None:
        if for_update:
            query = select(HostModel).with_for_update().filter_by(id=id)
        else:
            query = select(HostModel).filter_by(id=id)

        res = await self._session.execute(query)
        host = res.scalar()
        if not host:
            return

        return Host(
            id=host.id,
            user_id=host.user_id,
            domain=host.domain,
            active=host.active,
            action_number=host.action_number,
            created_at=host.created_at,
            updated_at=host.updated_at,
            user_signature=host.user_signature
        )

    @entity_storage
    async def get_by_user_id(self, user_id: int, *, for_update: bool = False) -> Host | None:
        if for_update:
            query = select(HostModel).with_for_update().filter_by(user_id=user_id)
        else:
            query = select(HostModel).filter_by(user_id=user_id)

        res = await self._session.execute(query)
        host = res.scalar()
        if not host:
            return

        return Host(
            id=host.id,
            user_id=host.user_id,
            domain=host.domain,
            active=host.active,
            action_number=host.action_number,
            created_at=host.created_at,
            updated_at=host.updated_at,
            user_signature=host.user_signature
        )

    async def fetch_related(self, host: Host) -> None:
        user = await self._user_repository.get_by_id(host.user_id)
        active_games = []
        for game_repository in self._game_repositories:
            active_games.extend(await game_repository.get_active_games(host.user_id))

        host.user = user
        host.active_games = active_games

    async def violated_constraint_unique_host(self, host: Host) -> None:
        query = select(HostModel).filter(HostModel.user_id == host.user_id, HostModel.id != host.id)
        res = await self._session.execute(query)
        existence_host = res.scalar()
        if existence_host:
            raise ViolatedConstraintError("Host already exists")

    async def violated_constraint_unique_domain(self, host: Host) -> None:
        query = select(HostModel).filter(HostModel.domain == host.domain, HostModel.user_id != host.user_id)
        res = await self._session.execute(query)
        existence_host = res.scalar()
        if existence_host:
            raise ViolatedConstraintError("Domain is already taken")
