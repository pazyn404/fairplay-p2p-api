from config import VerifyingKey
from .base import BaseEntity


class User(BaseEntity):
    DATA_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at"]

    def __init__(
            self,
            *,
            id: int | None = None,
            public_key: bytes,
            action_number: int = 0,
            balance: int = 0,
            created_at: int
    ) -> None:
        super().__init__()

        self.id = id
        self.public_key = public_key
        self.action_number = action_number
        self.balance = balance
        self.created_at = created_at

    def verify_public_key(self) -> None:
        VerifyingKey(self.public_key)
