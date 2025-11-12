from .base_game_without_relations import BaseGameWithoutRelationsResponseSchema


class OptimalStoppingGameWithoutRelationsResponseSchema(BaseGameWithoutRelationsResponseSchema):
    numbers_count: int
    mean: int
    std: int
    top: int
