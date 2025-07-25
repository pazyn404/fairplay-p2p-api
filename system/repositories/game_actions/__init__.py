from .optimal_stopping_host_action import OptimalStoppingHostActionRepository
from .optimal_stopping_player_action import OptimalStoppingPlayerActionRepository


game_host_action_repositories = {
    "optimal_stopping": OptimalStoppingHostActionRepository
}

game_player_action_repositories = {
    "optimal_stopping": OptimalStoppingPlayerActionRepository
}
