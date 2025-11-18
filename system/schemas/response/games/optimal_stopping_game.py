from .base_game import BaseGameResponseSchema, BaseGameActionResponseSchema


class OptimalStoppingPlayerActionResponseSchema(BaseGameActionResponseSchema):
    action: str


class OptimalStoppingHostActionResponseSchema(BaseGameActionResponseSchema):
    number: int


class OptimalStoppingGameResponseSchema(BaseGameResponseSchema):
    player_actions: list[OptimalStoppingPlayerActionResponseSchema]
    host_actions: list[OptimalStoppingHostActionResponseSchema]
    numbers_count: int
    mean: int
    std: int
    top: int
