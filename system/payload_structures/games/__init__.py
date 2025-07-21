from .create_optimal_stopping import create_optimal_stopping_game_structure
from .update_optimal_stopping import update_optimal_stopping_game_structure


create_game_structures = {
    "optimal_stopping": create_optimal_stopping_game_structure
}

update_game_structures = {
    "optimal_stopping": update_optimal_stopping_game_structure
}
