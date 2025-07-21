from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class HostModel(BaseModel):
    __tablename__ = "hosts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)
    domain: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    active: Mapped[bool] = mapped_column(nullable=False)
    action_number: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(nullable=False)
    updated_at: Mapped[int] = mapped_column(nullable=False)
    user_signature: Mapped[bytes] = mapped_column(nullable=False)
