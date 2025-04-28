from .user import User
from .host import Host
from .base_game import BaseGame
from .optimal_stopping_game import OptimalStoppingGame
from .optimal_stopping_system_action import OptimalStoppingSystemAction


game_models = {
    "optimal_stopping_game": OptimalStoppingGame
}

game_action_models = {
    "optimal_stopping_game": OptimalStoppingSystemAction
}

for game_model_name, game_model in game_models.items():
    game_system_action = game_action_models[game_model_name]

    game_system_action.GAME_MODEL = game_model
    game_model.SYSTEM_ACTION_MODEL = game_system_action
