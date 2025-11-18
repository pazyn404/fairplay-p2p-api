from pydantic import BaseModel, Base64Bytes, field_serializer


class CreateUserRequestSchema(BaseModel):
    public_key: Base64Bytes

    @field_serializer("public_key")
    def public_key_serializer(self, public_key: Base64Bytes) -> bytes:
        return public_key
