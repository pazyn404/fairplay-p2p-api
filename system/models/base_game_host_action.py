from sqlalchemy.orm import relationship, joinedload

from utils import sign
from .base_game_action import BaseGameAction


class BaseGameHostAction(BaseGameAction):
    __mapper_args__ = {
        "polymorphic_on": "type"
    }

    FOR_PLAYER_DATA_ATTRIBUTES = [
        "action_number|player.action_number", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at",
        "system_signature|for_player_signature"
    ]
    FOR_PLAYER_SIGNATURE_ATTRIBUTES = [
        "action_number|player.action_number", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]

    user = relationship("User", viewonly=True, uselist=False)
    player = relationship(
        "User",
        primaryjoin=f"BaseGame.id == BaseGameHostAction.game_id",
        secondaryjoin=f"User.id == BaseGame.player_id",
        secondary="base_game",
        viewonly=True,
        uselist=False
    )
    game = relationship("BaseGame", viewonly=True, uselist=False)

    @property
    def for_player_data(self):
        return self._parse_attrs(self.__class__.FOR_PLAYER_DATA_ATTRIBUTES)

    @property
    def for_player_signature_data(self):
        return self._parse_attrs(self.__class__.FOR_PLAYER_SIGNATURE_ATTRIBUTES)

    @property
    def for_player_signature(self):
        data = self.for_player_signature_data
        signature = sign(data)

        return signature

    def _options(self):
        return [
            joinedload(self.__class__.user),
            joinedload(self.__class__.player),
            joinedload(self.__class__.game)
        ]
