from entities import BaseGameAction
from models import BaseGameActionModel
from abstract_repositories import AbstractBaseGameActionRepository


class BaseGameActionRepository(AbstractBaseGameActionRepository):
    @staticmethod
    def _common_attrs(game_action: BaseGameAction | BaseGameActionModel) -> dict[str, bytes | str | int | None]:
        return {
            "id": game_action.id,
            "user_id": game_action.user_id,
            "game_id": game_action.game_id,
            "action_number": game_action.action_number,
            "game_action_number": game_action.game_action_number,
            "created_at": game_action.created_at,
            "user_signature": game_action.user_signature,
        }
