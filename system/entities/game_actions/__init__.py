from .base_game_action import BaseGameAction
from .base_game_host_action import BaseGameHostAction
from .base_game_player_action import BaseGamePlayerAction
from .optimal_stopping_host_action import OptimalStoppingHostAction
from .optimal_stopping_player_action import OptimalStoppingPlayerAction


game_host_action_entities = {
    "optimal_stopping": OptimalStoppingHostAction
}

game_player_action_entities = {
    "optimal_stopping": OptimalStoppingPlayerAction
}
