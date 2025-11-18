from pydantic import Field, Base64Bytes, field_serializer

from ...attribute_model import AttributeModel


class BaseGameActionResponseSchema(AttributeModel):
    id: int
    user_id: int
    action_number: int
    game_action_number: int
    created_at: int
    system_signature: bytes

    @field_serializer("system_signature")
    def system_signature_serializer(self, system_signature: bytes) -> Base64Bytes:
        return system_signature


class BaseGameResponseSchema(AttributeModel):
    id: int
    user_id: int
    player_id: int | None
    winner_id: int | None
    action_number: int
    game_name: str = Field(alias="GAME_NAME")
    bet: int
    duration: int
    active: bool
    seed: bytes | None
    seed_hash: bytes
    started_at: int | None
    finished_at: int | None
    created_at: int
    updated_at: int
    system_signature: bytes

    @field_serializer("seed")
    def seed_serializer(self, seed: bytes | None) -> Base64Bytes | None:
        if seed is not None:
            return seed

        return None

    @field_serializer("seed_hash")
    def seed_hash_serializer(self, seed_hash: bytes) -> Base64Bytes:
        return seed_hash

    @field_serializer("system_signature")
    def system_signature_serializer(self, system_signature: bytes) -> Base64Bytes:
        return system_signature
