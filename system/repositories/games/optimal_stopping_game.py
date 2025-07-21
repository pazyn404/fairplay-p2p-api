from sqlalchemy import select

from entities import OptimalStoppingGame
from models import OptimalStoppingGameModel
from decorators import entity_storage
from context import postgres_session
from .base_game import BaseGameRepository


class OptimalStoppingGameRepository(BaseGameRepository):
    def __init__(self, *, primary: bool = True) -> None:
        from ..game_actions import OptimalStoppingHostActionRepository
        from ..game_actions import OptimalStoppingPlayerActionRepository

        super().__init__(primary=primary)

        self._session = postgres_session.get()
        if primary:
            self._host_action_repository = OptimalStoppingHostActionRepository(primary=False)
            self._player_action_repository = OptimalStoppingPlayerActionRepository(primary=False)

    async def save(self, game: OptimalStoppingGame) -> None:
        if game.id is None:
            game_orm = OptimalStoppingGameModel(
                **self.__class__._common_attrs(game),
                numbers_count=game.numbers_count,
                mean=game.mean,
                std=game.std,
                top=game.top
            )

            self._session.add(game_orm)
            await self._session.flush()

            game.id = game_orm.id
        else:
            game_orm = await self._session.get(OptimalStoppingGameModel, game.id)

            game_orm.update(
                **self.__class__._common_attrs(game),
                numbers_count=game.numbers_count,
                mean=game.mean,
                std=game.std,
                top=game.top
            )

    @entity_storage
    async def get_by_id(self, id: int, *, for_update: bool = False) -> OptimalStoppingGame | None:
        if for_update:
            query = select(OptimalStoppingGameModel).with_for_update().filter_by(id=id)
        else:
            query = select(OptimalStoppingGameModel).filter_by(id=id)

        res = await self._session.execute(query)
        game = res.scalar()
        if not game:
            return

        return OptimalStoppingGame(
            **self.__class__._common_attrs(game),
            numbers_count=game.numbers_count,
            mean=game.mean,
            std=game.std,
            top=game.top
        )

    @entity_storage
    async def get_active_games(self, user_id: int) -> list[OptimalStoppingGame]:
        query = select(OptimalStoppingGameModel).filter(
            OptimalStoppingGameModel.user_id == user_id,
            OptimalStoppingGameModel.active == True,
            OptimalStoppingGameModel.winner_id.is_(None)
        )
        res = await self._session.execute(query)
        games = res.scalars().all()

        return [
            OptimalStoppingGame(
                **self.__class__._common_attrs(game),
                numbers_count=game.numbers_count,
                mean=game.mean,
                std=game.std,
                top=game.top

            ) for game in games
        ]

    @entity_storage
    async def get_all_active_games(self) -> list[OptimalStoppingGame]:
        query = select(OptimalStoppingGameModel).filter(
            OptimalStoppingGameModel.active == True,
            OptimalStoppingGameModel.player_id.is_(None)
        )
        res = await self._session.execute(query)
        games = res.scalars().all()

        return [
            OptimalStoppingGame(
                **self.__class__._common_attrs(game),
                numbers_count=game.numbers_count,
                mean=game.mean,
                std=game.std,
                top=game.top
            ) for game in games
        ]
