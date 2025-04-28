from .user import User
from .host import Host
from .optimal_stopping_game import OptimalStoppingGame
from .optimal_stopping_host_action import OptimalStoppingHostAction
from .optimal_stopping_player_action import OptimalStoppingPlayerAction


game_models = {
    "optimal_stopping_game": OptimalStoppingGame
}

game_action_models = {
    "optimal_stopping_game": {
        "player_action": OptimalStoppingPlayerAction,
        "host_action": OptimalStoppingHostAction
    }
}


for game_model_name, game_model in game_models.items():
    player_action_model, host_action_model = game_action_models[game_model_name]["player_action"], game_action_models[game_model_name]["host_action"]

    player_action_model.GAME_MODEL = game_model
    host_action_model.GAME_MODEL = game_model
    game_model.PLAYER_ACTION_MODEL = player_action_model
    game_model.HOST_ACTION_MODEL = host_action_model
