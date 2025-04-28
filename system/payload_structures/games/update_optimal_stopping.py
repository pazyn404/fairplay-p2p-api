structure = {
    "id": {
        "type": int
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
    "seed_hash": {
        "type": str,
        "encoding": "base64",
        "optional": True
    },
    "numbers_count": {
        "type": int,
        "gte": 10,
        "lte": 20,
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
        "lte": 10,
        "optional": True
    },
    "user_signature": {
        "type": str,
        "encoding": "base64"
    }
}
