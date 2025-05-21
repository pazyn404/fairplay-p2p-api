from .user import User
from .host import Host
from .base_game import BaseGame
from .optimal_stopping_game import OptimalStoppingGame
from .optimal_stopping_host_action import OptimalStoppingHostAction
from .optimal_stopping_player_action import OptimalStoppingPlayerAction


game_models = {
    "optimal_stopping_game": OptimalStoppingGame
}

game_host_action_models = {
    "optimal_stopping_game": OptimalStoppingHostAction
}

game_player_action_models = {
    "optimal_stopping_game": OptimalStoppingPlayerAction
}
