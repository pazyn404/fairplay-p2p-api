from entities import BaseGame
from models import BaseGameModel
from abstract_repositories import AbstractBaseGameRepository


class BaseGameRepository(AbstractBaseGameRepository):
    def __init__(self, *, primary: bool) -> None:
        from ..user import UserRepository
        from ..host import HostRepository

        if primary:
            self._user_repository = UserRepository(primary=False)
            self._host_repository = HostRepository(primary=False)

    async def fetch_related(self, game: BaseGame) -> None:
        user = await self._user_repository.get_by_id(game.user_id)
        host = await self._host_repository.get_by_user_id(game.user_id)
        host_actions = await self._host_action_repository.get_by_game_id(game.id)
        player_actions = await self._player_action_repository.get_by_game_id(game.id)

        for host_action in host_actions:
            host_action.game = game
        for player_action in player_actions:
            player_action.game = game

        game.user = user
        game.host = host
        game.host_actions = host_actions
        game.player_actions = player_actions

    @staticmethod
    def _common_attrs(game: BaseGame | BaseGameModel) -> dict[str, bytes | str | int | None]:
        return {
            "id": game.id,
            "user_id": game.user_id,
            "player_id": game.player_id,
            "winner_id": game.winner_id,
            "action_number": game.action_number,
            "game_action_number": game.game_action_number,
            "bet": game.bet,
            "duration": game.duration,
            "active": game.active,
            "seed_hash": game.seed_hash,
            "seed": game.seed,
            "created_at": game.created_at,
            "updated_at": game.updated_at,
            "started_at": game.started_at,
            "finished_at": game.finished_at,
            "user_signature": game.user_signature,
            "paid_out": game.paid_out
        }
