from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from config import VerifyingKey
from .base_model import BaseModel


class User(BaseModel):
    DATA_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at"]

    id: Mapped[int] = mapped_column(primary_key=True)
    public_key: Mapped[bytes] = mapped_column(nullable=False)
    action_number: Mapped[int] = mapped_column(nullable=False, default=1)
    balance: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[int] = mapped_column(nullable=False)

    def verify_public_key(self):
        VerifyingKey(self.public_key)
