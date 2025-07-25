from exceptions import VerificationError
from mixins import VerifySignatureMixin, UpdateRelatedUserActionNumberMixin
from .base import BaseEntity


class Host(VerifySignatureMixin, UpdateRelatedUserActionNumberMixin, BaseEntity):
    DATA_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at"]
    USER_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active"]

    def __init__(
            self,
            *,
            id: int | None = None,
            user_id: int,
            domain: str,
            active: bool,
            action_number: int | None = None,
            created_at: int,
            updated_at: int,
            user_signature: bytes
    ) -> None:
        super().__init__()

        self.id = id
        self.user_id = user_id
        self.domain = domain
        self.active = active
        self.action_number = action_number
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_signature = user_signature

        self.user = None
        self.active_games = None

    def fill_from_related(self) -> None:
        self.action_number = self.user.action_number

    def verify_turn_off(self) -> None:
        if not self.active and self.active_games:
            raise VerificationError("Host can't be turned off during active or pending games", 409)

    def verify_domain_change(self, prev_domain: str | None, prev_active: bool | None) -> None:
        if not prev_domain or not self.active or not prev_active:
            return

        if self.domain != prev_domain:
            raise VerificationError("Host must be turned off to change domain", 409)
