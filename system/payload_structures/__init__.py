from .create_user import structure as create_user_structure
from .create_host import structure as create_host_structure
from .update_host import structure as update_host_structure
from .games import create_structures as create_game_structures
from .games import update_structures as update_game_structures
from .game_actions import host_structures as game_host_action_structures
from .game_actions import player_structures as game_player_action_structures
from .reveal_setup import structure as reveal_setup_structure


create_structures = {
    "user": create_user_structure,
    "host": create_host_structure,
    **create_game_structures
}

update_structures = {
    "host": update_host_structure,
    **update_game_structures
}
