from pydantic import BaseModel, Base64Bytes, field_serializer


class HostRevealSetupResponseSchema(BaseModel):
    seed: Base64Bytes
    user_signature: Base64Bytes

    @field_serializer("seed")
    def seed_serializer(self, seed: Base64Bytes) -> bytes:
        return seed

    @field_serializer("user_signature")
    def user_signature_serializer(self, user_signature: Base64Bytes) -> bytes:
        return user_signature
