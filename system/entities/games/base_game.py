from abc import abstractmethod
from hashlib import sha256

from exceptions import VerificationError
from mixins import VerifySignatureMixin, UpdateRelatedUserActionNumberMixin
from ..base import BaseEntity


class BaseGame(VerifySignatureMixin, UpdateRelatedUserActionNumberMixin, BaseEntity):
    DATA_ATTRIBUTES = [
        "id", "user_id", "player_id", "winner_id", "action_number", "game_name|GAME_NAME", "bet", "duration",
        "active", "seed_hash", "seed", "started_at", "finished_at", "created_at", "updated_at",
        "player_actions|player_actions.data", "host_actions|host_actions.data", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "player_id", "winner_id", "action_number", "game_action_number", "game_name|GAME_NAME", "bet",
        "duration", "active", "seed_hash", "seed", "started_at", "finished_at", "created_at", "updated_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|GAME_NAME", "bet", "duration", "active", "seed_hash", "seed"
    ]

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
