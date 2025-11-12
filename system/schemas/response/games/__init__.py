from .optimal_stopping_game import OptimalStoppingGameResponseSchema
from .optimal_stopping_game_without_relations import OptimalStoppingGameWithoutRelationsResponseSchema


game_response_schemas = {
    "optimal_stopping": OptimalStoppingGameResponseSchema
}

game_without_relations_response_schemas = {
    "optimal_stopping": OptimalStoppingGameWithoutRelationsResponseSchema
}
