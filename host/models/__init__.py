from .user import User
from .host import Host
from .base_game import BaseGame
from .optimal_stopping_game import OptimalStoppingGame
from .optimal_stopping_system_action import OptimalStoppingSystemAction


game_models = {
    "optimal_stopping_game": OptimalStoppingGame
}

game_system_action_models = {
    "optimal_stopping_game": OptimalStoppingSystemAction
}
