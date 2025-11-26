from typing import Annotated

from pydantic import BaseModel, Field, Base64Bytes, field_serializer


class BaseUpdateGameRequestSchema(BaseModel):
    id: int
    bet: Annotated[int, Field(gt=0)] | None = None
    duration: Annotated[int, Field(gt=9, lt=301)] | None = None
    active: bool | None = None
    seed_hash: Base64Bytes | None = None
    user_signature: Base64Bytes

    @field_serializer("seed_hash")
    def seed_hash_serializer(self, seed_hash: Base64Bytes | None) -> bytes | None:
        return seed_hash

    @field_serializer("user_signature")
    def user_signature_serializer(self, user_signature: Base64Bytes) -> bytes:
        return user_signature
