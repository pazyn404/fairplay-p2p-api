from sqlalchemy import select

from entities import OptimalStoppingHostAction
from models import OptimalStoppingHostActionModel
from decorators import entity_storage
from context import postgres_session
from .base_game_host_action import BaseGameHostActionRepository


class OptimalStoppingHostActionRepository(BaseGameHostActionRepository):
    def __init__(self, *, primary: bool = True) -> None:
        from ..games import OptimalStoppingGameRepository

        super().__init__(primary=primary)

        self._session = postgres_session.get()
        if primary:
            self._game_repository = OptimalStoppingGameRepository(primary=False)

    async def save(self, game_action: OptimalStoppingHostAction) -> None:
        game_action_orm = OptimalStoppingHostActionModel(
            **self.__class__._common_attrs(game_action),
            number=game_action.number
        )

        self._session.add(game_action_orm)
        await self._session.flush()

        game_action.id =  game_action_orm.id

    @entity_storage
    async def get_by_game_id(self, game_id: int) -> list[OptimalStoppingHostAction]:
        query = select(OptimalStoppingHostActionModel).filter_by(game_id=game_id)
        res = await self._session.execute(query)
        game_actions = res.scalars().all()

        return [
            OptimalStoppingHostAction(
                **self.__class__._common_attrs(game_action),
                number=game_action.number
            ) for game_action in game_actions
        ]
