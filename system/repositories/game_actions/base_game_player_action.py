from entities import BaseGameAction
from .base_game_action import BaseGameActionRepository


class BaseGamePlayerActionRepository(BaseGameActionRepository):
    def __init__(self, *, primary: bool) -> None:
        from ..user import UserRepository
        from ..host import HostRepository

        if primary:
            self._user_repository = UserRepository(primary=False)
            self._host_repository = HostRepository(primary=False)

    async def fetch_related(self, game_action: BaseGameAction) -> None:
        game = await self._game_repository.get_by_id(game_action.game_id)
        user = await self._user_repository.get_by_id(game_action.user_id)
        player_host = await self._host_repository.get_by_user_id(game_action.user_id)
        host_user = await self._user_repository.get_by_id(game.user_id)
        host = await self._host_repository.get_by_user_id(game.user_id)

        game_action.game = game
        game_action.user = user
        game_action.player_host = player_host
        game_action.host_user = host_user
        game_action.host = host
