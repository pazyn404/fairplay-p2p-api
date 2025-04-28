from .create_optimal_stopping import structure as create_optimal_stopping_game_structure
from .update_optimal_stopping import structure as update_optimal_stopping_game_structure


create_structures = {
    "optimal_stopping_game": create_optimal_stopping_game_structure
}

update_structures = {
    "optimal_stopping_game": update_optimal_stopping_game_structure
}
