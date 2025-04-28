from .optimal_stopping_player_action import structure as optimal_stopping_player_action
from .optimal_stopping_host_action import structure as optimal_stopping_host_action


structures = {
    "optimal_stopping_game": {
        "player_action": optimal_stopping_player_action,
        "host_action": optimal_stopping_host_action
    }
}
