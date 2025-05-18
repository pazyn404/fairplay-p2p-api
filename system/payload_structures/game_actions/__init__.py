from .optimal_stopping_player_action import structure as optimal_stopping_player_action
from .optimal_stopping_host_action import structure as optimal_stopping_host_action


host_structures = {
    "optimal_stopping_game": optimal_stopping_host_action
}

player_structures = {
    "optimal_stopping_game": optimal_stopping_player_action
}
