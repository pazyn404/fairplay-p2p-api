from .base_create_game import BaseCreateGameRequestSchema
from .base_update_game import BaseUpdateGameRequestSchema
from .create_optimal_stopping_game import CreateOptimalStoppingGameRequestSchema
from .update_optimal_stopping_game import UpdateOptimalStoppingGameRequestSchema


create_game_request_schemas = {
    "optimal_stopping": CreateOptimalStoppingGameRequestSchema
}

update_game_request_schemas = {
    "optimal_stopping": UpdateOptimalStoppingGameRequestSchema
}
