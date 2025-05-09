structure = {
    "id": {
        "type": int
    },
    "domain": {
        "type": str,
        "optional": True
    },
    "active": {
        "type": bool,
        "optional": True
    },
    "user_signature": {
        "type": str,
        "encoding": "base64"
    }
}
