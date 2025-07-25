update_optimal_stopping_game_structure = {
    "id": {
        "type": int
    },
    "seed": {
        "type": str,
        "encoding": "base64",
        "optional": True
    },
    "bet": {
        "type": int,
        "gt": 0,
        "optional": True
    },
    "duration": {
        "type": int,
        "gte": 10,
        "lte": 300,
        "optional": True
    },
    "active": {
        "type": bool,
        "optional": True
    },
    "numbers_count": {
        "type": int,
        "gte": 10,
        "lte": 50,
        "optional": True
    },
    "std": {
        "type": int,
        "gte": 100,
        "lte": 1000,
        "optional": True
    },
    "mean": {
        "type": int,
        "gte": 0,
        "lte": 1000,
        "optional": True
    },
    "top": {
        "type": int,
        "gte": 1,
        "lte": 50,
        "optional": True
    }
}
