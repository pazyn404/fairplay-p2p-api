from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_key: Mapped[bytes] = mapped_column(nullable=False)
    action_number: Mapped[int] = mapped_column(nullable=False)
    balance: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
