from abc import abstractmethod

from exceptions import VerificationError
from mixins import UpdateRelatedUserActionNumberMixin
from utils import sign
from .base_game_action import BaseGameAction


class BaseGamePlayerAction(UpdateRelatedUserActionNumberMixin, BaseGameAction):
    FOR_HOST_DATA_ATTRIBUTES = ["game_id", "created_at", "system_signature|for_host_signature"]
    FOR_HOST_SIGNATURE_ATTRIBUTES = [
        "action_number|host_user.action_number", "game_id", "game_name|game.__class__.GAME_NAME",
        "game_revision|game.action_number", "game_action_number", "created_at"
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.game = None
        self.user = None
        self.player_host = None
        self.host_user = None
        self.host = None

    @property
    def for_host_data(self) -> dict:
        return self._parse_attrs(self.__class__.FOR_HOST_DATA_ATTRIBUTES)

    @property
    def for_host_signature_data(self) -> dict:
        return self._parse_attrs(self.__class__.FOR_HOST_SIGNATURE_ATTRIBUTES)

    @property
    def for_host_signature(self) -> bytes:
        data = self.for_host_signature_data
        signature = sign(data)

        return signature

    @abstractmethod
    def is_last_action(self) -> bool:
        raise NotImplementedError

    def is_first_action(self) -> bool:
        return self.game.game_action_number == 1

    def verify_player_balance(self) -> None:
        if self.user.balance < 0:
            raise VerificationError("Insufficient balance", 409)

    def verify_player_host_unset(self) -> None:
        if self.player_host:
            raise VerificationError("You can't play from an account where a host is set", 409)

    def verify_player(self) -> None:
        if self.game.player_id is not None and self.game.player_id != self.user_id:
            raise VerificationError("You are not player of this game", 409)

    def verify_host_active(self) -> None:
        if not self.host.active:
            raise VerificationError("Host is not active", 409)

    def verify_game_active(self) -> None:
        if not self.game.active:
            raise VerificationError("Game is not active", 409)

    def verify_game_not_complete(self) -> None:
        if (self.game.winner_id is not None or
                (self.game.started_at is not None and self.game.started_at + self.game.duration < self.created_at)):
            raise VerificationError("Game is already complete", 409)

    def update_related_player_balance(self) -> None:
        if self.is_first_action():
            self.user.balance -= self.game.bet

    def update_related_game_action_number(self) -> None:
        self.game.game_action_number += 1

    def update_related_game_player(self) -> None:
        if self.is_first_action():
            self.game.player_id = self.user_id

    def update_related_game_started_time(self) -> None:
        if self.is_first_action():
            self.game.started_at = self.created_at

    def update_related_game_finished_time(self) -> None:
        if self.is_last_action():
            self.game.finished_at = self.created_at
