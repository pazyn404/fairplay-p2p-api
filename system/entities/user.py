from base64 import b64encode

from  keys import VerifyingKey
from .base import BaseEntity


class User(BaseEntity):
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

    @property
    def system_signature_data(self) -> dict[str, int | str]:
        return {
            "id": self.id,
            "public_key": b64encode(self.public_key).decode(),
            "action_number": self.action_number,
            "balance": self.balance,
            "created_at": self.created_at
        }

    def verify_public_key(self) -> None:
        VerifyingKey(self.public_key)
