from abc import abstractmethod

from sqlalchemy.orm import relationship, joinedload

from config import VerificationError
from mixins import UpdateRelatedUserActionNumberMixin
from utils import sign
from .base_game_action import BaseGameAction


class BaseGamePlayerAction(UpdateRelatedUserActionNumberMixin, BaseGameAction):
    __mapper_args__ = {
        "polymorphic_on": "type"
    }

    FOR_HOST_DATA_ATTRIBUTES = ["game_id", "created_at", "system_signature|for_host_signature"]
    FOR_HOST_SIGNATURE_ATTRIBUTES = [
        "action_number|host_user.action_number", "game_id", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]

    user = relationship("User", uselist=False)
    host_user = relationship(
        "User",
        primaryjoin=f"BaseGame.id == BaseGamePlayerAction.game_id",
        secondaryjoin=f"User.id == BaseGame.user_id",
        secondary="base_game",
        viewonly=True,
        uselist=False
    )
    host = relationship(
        "Host",
        primaryjoin=f"BaseGame.id == BaseGamePlayerAction.game_id",
        secondaryjoin=f"Host.user_id == BaseGame.user_id",
        secondary="base_game",
        viewonly=True,
        uselist=False
    )
    player_host = relationship(
        "Host",
        primaryjoin=f"BaseGame.id == BaseGamePlayerAction.game_id",
        secondaryjoin=f"Host.user_id == BaseGame.player_id",
        secondary="base_game",
        viewonly=True,
        uselist=False
    )
    game = relationship("BaseGame", uselist=False)

    @abstractmethod
    def is_last_action(self):
        raise NotImplementedError

    def is_first_action(self):
        return self.game_action_number == 1

    @property
    def for_host_data(self):
        return self._parse_attrs(self.__class__.FOR_HOST_DATA_ATTRIBUTES)

    @property
    def for_host_signature_data(self):
        return self._parse_attrs(self.__class__.FOR_HOST_SIGNATURE_ATTRIBUTES)

    @property
    def for_host_signature(self):
        data = self.for_host_signature_data
        signature = sign(data)

        return signature

    def _options(self):
        return [
            joinedload(self.__class__.user),
            joinedload(self.__class__.host_user),
            joinedload(self.__class__.host),
            joinedload(self.__class__.player_host),
            joinedload(self.__class__.game)
        ]

    def verify_player_balance(self):
        if self.game.player_id is not None:
            return

        if self.user.balance < self.game.bet:
            raise VerificationError("Insufficient balance", 409)

    def verify_player_host_unset(self):
        if self.player_host:
            raise VerificationError("You can't play from an account where a host is set", 409)

    def verify_player(self):
        if self.game.player_id is not None and self.game.player_id != self.user_id:
            raise VerificationError("You are not player of this game", 409)

    def verify_host_active(self):
        if not self.host.active:
            raise VerificationError("Host is not active", 409)

    def verify_game_active(self):
        if not self.game.active:
            raise VerificationError("Game is not active", 409)

    def verify_game_not_complete(self):
        if (self.game.winner_id is not None or
                (self.game.started_at is not None and self.game.started_at + self.game.duration < self.created_at)):
            raise VerificationError("Game is already complete", 409)

    def update_related_player_balance(self):
        if self.is_first_action():
            self.user.balance -= self.game.bet

    def update_related_game_actions_count(self):
        self.game.actions_count += 1

    def update_related_game_started_time(self):
        if self.is_first_action():
            self.game.started_at = self.created_at

    def update_related_game_finished_time(self):
        if self.is_last_action():
            self.game.finished_at = self.created_at
