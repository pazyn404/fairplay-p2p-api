from pydantic import Base64Bytes, field_serializer

from ..attribute_model import AttributeModel


class UserResponseSchema(AttributeModel):
    id: int
    public_key: bytes
    action_number: int
    balance: int
    created_at: int
    system_signature: bytes

    @field_serializer("public_key")
    def public_key_serializer(self, public_key: bytes) -> Base64Bytes:
        return public_key

    @field_serializer("system_signature")
    def system_signature_serializer(self, system_signature: bytes) -> Base64Bytes:
        return system_signature
