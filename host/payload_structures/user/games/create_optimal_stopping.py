structure = {
    "user_id": {
        "type": int
    },
    "seed": {
        "type": str,
        "encoding": "base64"
    },
    "bet": {
        "type": int,
        "gt": 0
    },
    "duration": {
        "type": int,
        "gte": 10,
        "lte": 300
    },
    "active": {
        "type": bool
    },
    "numbers_count": {
        "type": int,
        "gte": 10,
        "lte": 20
    },
    "std": {
        "type": int,
        "gte": 100,
        "lte": 1000
    },
    "mean": {
        "type": int,
        "gte": 0,
        "lte": 1000
    },
    "top": {
        "type": int,
        "gte": 1,
        "lte": 5
    }
}
