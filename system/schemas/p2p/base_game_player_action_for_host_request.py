from base64 import b64encode

from pydantic import Field, Base64Bytes, field_serializer

from ..attribute_model import AttributeModel



class BaseGamePlayerActionForHostRequestSchema(AttributeModel):
    game_id: int
    created_at: int
    system_signature: bytes = Field(alias="for_host_system_signature")

    @field_serializer("system_signature")
    def system_signature_serializer(self, system_signature: bytes) -> str:
        return b64encode(system_signature).decode()
