from entities import BaseGameAction
from .base_game_action import BaseGameActionRepository


class BaseGameHostActionRepository(BaseGameActionRepository):
    def __init__(self, *, primary: bool) -> None:
        from ..user import UserRepository

        if primary:
            self._user_repository = UserRepository(primary=False)

    async def fetch_related(self, game_action: BaseGameAction) -> None:
        game = await self._game_repository.get_by_id(game_action.game_id)
        user = await self._user_repository.get_by_id(game.user_id)
        player = await self._user_repository.get_by_id(game.player_id)

        game_action.game = game
        game_action.user = user
        game_action.player = player
