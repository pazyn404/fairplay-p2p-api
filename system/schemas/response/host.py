from pydantic import Base64Bytes, field_serializer

from ..attribute_model import AttributeModel


class HostResponseSchema(AttributeModel):
    id: int
    user_id: int
    action_number: int
    domain: str
    active: bool
    created_at: int
    updated_at: int
    system_signature: bytes

    @field_serializer("system_signature")
    def system_signature_serializer(self, system_signature: bytes) -> Base64Bytes:
        return system_signature
