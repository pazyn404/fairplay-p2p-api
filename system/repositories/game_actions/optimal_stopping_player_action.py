from sqlalchemy import select

from entities import OptimalStoppingPlayerAction
from models import OptimalStoppingPlayerActionModel
from decorators import entity_storage
from context import postgres_session
from .base_game_player_action import BaseGamePlayerActionRepository


class OptimalStoppingPlayerActionRepository(BaseGamePlayerActionRepository):
    def __init__(self, *, primary: bool = True) -> None:
        from ..games.optimal_stopping_game import OptimalStoppingGameRepository

        super().__init__(primary=primary)

        self._session = postgres_session.get()
        if primary:
            self._game_repository = OptimalStoppingGameRepository(primary=False)

    async def save(self, game_action: OptimalStoppingPlayerAction) -> None:
        game_action_orm = OptimalStoppingPlayerActionModel(
            **self.__class__._common_attrs(game_action),
            action=game_action.action
        )

        self._session.add(game_action_orm)
        await self._session.flush()

        game_action.id = game_action_orm.id

    @entity_storage
    async def get_by_game_id(self, game_id: int) -> list[OptimalStoppingPlayerAction]:
        query = select(OptimalStoppingPlayerActionModel).filter_by(game_id=game_id)
        res = await self._session.execute(query)
        game_actions = res.scalars().all()

        return [
            OptimalStoppingPlayerAction(
                **self.__class__._common_attrs(game_action),
                action=game_action.action
            ) for game_action in game_actions
        ]
