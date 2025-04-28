from .update_host import structure as update_host_structure
from .games import create_structures as create_game_structures
from .games import update_structures as update_game_structures


create_structures = {
    **create_game_structures
}

update_structures = {
    "host": update_host_structure,
    **update_game_structures
}
