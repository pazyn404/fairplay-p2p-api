from typing import Annotated

from pydantic import BaseModel, Field, Base64Bytes, field_serializer


class BaseCreateGameRequestSchema(BaseModel):
    user_id: int
    bet: Annotated[int, Field(gt=0)]
    duration: Annotated[int, Field(gt=10, lt=300)]
    active: bool
    active: bool
    seed_hash: Base64Bytes
    user_signature: Base64Bytes

    @field_serializer("seed_hash")
    def seed_hash_serializer(self, seed_hash: Base64Bytes) -> bytes:
        return seed_hash

    @field_serializer("user_signature")
    def user_signature_serializer(self, user_signature: Base64Bytes) -> bytes:
        return user_signature
