from pydantic import BaseModel, Base64Bytes, field_serializer


class UpdateHostRequestSchema(BaseModel):
    id: int
    domain: str | None = None
    active: bool | None = None
    user_signature: Base64Bytes

    @field_serializer("user_signature")
    def user_signature_serializer(self, user_signature: Base64Bytes) -> bytes:
        return user_signature
