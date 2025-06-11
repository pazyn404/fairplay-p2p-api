from sqlalchemy import LargeBinary, select
from sqlalchemy.orm import Mapped, mapped_column

from config import VerifyingKey
from .base_model import BaseModel
from config import ViolatedConstraintError


class User(BaseModel):
    DATA_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at"]

    id: Mapped[int] = mapped_column(primary_key=True)
    public_key: Mapped[bytes] = mapped_column(nullable=False, unique=True, index=True)
    action_number: Mapped[int] = mapped_column(nullable=False, default=1)
    balance: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[int] = mapped_column(nullable=False)

    async def violated_constraint_unique_public_key(self, session):
        query = select(User).filter(User.public_key == self.public_key, User.id != self.id)
        res = await session.execute(query)
        existence_user = res.scalars().first()
        if existence_user:
            raise ViolatedConstraintError("Insecure public key")

    def verify_public_key(self):
        VerifyingKey(self.public_key)
