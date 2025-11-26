from abc import ABC, abstractmethod
from hashlib import sha256
from base64 import b64encode

from exceptions import VerificationError
from mixins import VerifyUserSignatureMixin, UpdateRelatedUserActionNumberMixin
from ..base import BaseEntity


class BaseGame(ABC, VerifyUserSignatureMixin, UpdateRelatedUserActionNumberMixin, BaseEntity):
    def __init__(
            self,
            *,
            id: int = None,
            user_id: int,
            player_id: int | None = None,
            winner_id: int | None = None,
            action_number: int | None = None,
            game_action_number: int = 0,
            bet: int,
            duration: int,
            active: bool,
            seed_hash: bytes,
            seed: bytes | None = None,
            created_at: int,
            updated_at: int,
            started_at: int | None = None,
            finished_at: int | None = None,
            user_signature: bytes,
            paid_out: bool = False
    ) -> None:
        super().__init__()

        self.id = id
        self.user_id = user_id
        self.player_id = player_id
        self.winner_id = winner_id
        self.action_number = action_number
        self.game_action_number = game_action_number
        self.bet = bet
        self.duration = duration
        self.active = active
        self.seed_hash = seed_hash
        self.seed = seed
        self.created_at = created_at
        self.updated_at = updated_at
        self.started_at = started_at
        self.finished_at = finished_at
        self.user_signature = user_signature
        self.paid_out = paid_out

        self.user = None
        self.host = None
        self.player_actions = None
        self.host_actions = None

    @property
    def user_signature_data(self) -> dict[str, int | str | None]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_number": self.action_number,
            "game_name": self.__class__.GAME_NAME,
            "bet": self.bet,
            "duration": self.duration,
            "active": self.active,
            "seed_hash": b64encode(self.seed_hash).decode(),
            "seed": b64encode(self.seed).decode() if self.seed is not None else None
        }

    @property
    def system_signature_data(self) -> dict[str, int | str | None]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "player_id": self.player_id,
            "winner_id": self.winner_id,
            "action_number": self.action_number,
            "game_action_number": self.game_action_number,
            "game_name": self.__class__.GAME_NAME,
            "bet": self.bet,
            "duration": self.duration,
            "active": self.active,
            "seed_hash": b64encode(self.seed_hash).decode(),
            "seed": b64encode(self.seed).decode() if self.seed is not None else None,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def fill_from_related(self) -> None:
        self.action_number = self.user.action_number

    @abstractmethod
    def player_win(self) -> bool:
        raise NotImplementedError

    def complete(self) -> None:
        if self.player_win():
            self.winner_id = self.player_id
        else:
            self.winner_id = self.user_id

    def verify_seed_hash(self) -> None:
        if self.seed is None:
            return

        if sha256(self.seed).digest() != self.seed_hash:
            raise VerificationError("Seed hash does not match", 409)

    def verify_host_exist(self) -> None:
        if not self.host:
            raise VerificationError("Host is not set up", 409)

    def verify_host_active(self) -> None:
        if not self.host:
            return

        if not self.host.active and self.active:
            raise VerificationError("Host is not active", 409)

    def verify_pending(self) -> None:
        if self.winner_id is not None:
            raise VerificationError("Game is already complete", 409)
        if self.player_id is not None:
            raise VerificationError("Game has been started", 409)

    def verify_user_balance(self) -> None:
        if self.user.balance < 0:
            raise VerificationError("Insufficient balance", 409)

    def update_related_user_balance(self, prev_bet: int | None, prev_active: int | None) -> None:
        if self.active:
            if prev_active:
                self.user.balance -= self.bet - prev_bet
            else:
                self.user.balance -= self.bet
        else:
            if prev_active:
                self.user.balance += prev_bet
