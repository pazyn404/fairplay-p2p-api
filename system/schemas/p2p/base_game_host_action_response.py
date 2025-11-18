from pydantic import Base64Bytes, field_serializer

from ..attribute_model import AttributeModel


class BaseGameHostActionResponseSchema(AttributeModel):
    user_signature: Base64Bytes

    @field_serializer("user_signature")
    def user_signature_serializer(self, user_signature: Base64Bytes) -> bytes:
        return user_signature