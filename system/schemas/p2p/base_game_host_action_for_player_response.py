from pydantic import Base64Bytes, Field, field_serializer

from ..attribute_model import AttributeModel


class BaseGameHostActionForPlayerResponseSchema(AttributeModel):
    created_at: int
    system_signature: bytes = Field(alias="for_player_system_signature")

    @field_serializer("system_signature")
    def system_signature_serializer(self, system_signature: bytes) -> Base64Bytes:
        return system_signature
