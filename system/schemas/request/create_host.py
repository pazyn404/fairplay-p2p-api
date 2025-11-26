from pydantic import BaseModel, Base64Bytes, field_serializer


class CreateHostRequestSchema(BaseModel):
    user_id: int
    domain: str
    active: bool
    user_signature: Base64Bytes

    @field_serializer("user_signature")
    def user_signature_serializer(self, user_signature: Base64Bytes) -> bytes:
        return user_signature
