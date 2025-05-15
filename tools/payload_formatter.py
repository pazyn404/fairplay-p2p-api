import os
import sys
import json
import secrets
from hashlib import sha256
from base64 import b64encode, b64decode

from ecdsa import SigningKey


def sign(payload: dict) -> str:
    message = json.dumps(payload, separators=(",", ":"))
    signature = signing_key.sign(message.encode())

    return b64encode(signature).decode()


def generate_seed() -> str:
    seed = secrets.token_bytes(16)

    return b64encode(seed).decode()


def get_seed_hash(seed: str) -> str:
    seed = b64decode(seed.encode())
    seed_hash = sha256(seed).digest()

    return b64encode(seed_hash).decode()

who = sys.argv[1]
user_id = int(sys.argv[2])
action_number = int(sys.argv[3])

if who == "player":
    private_key_path = "../player/keys/player_private_key.der"
else:
    private_key_path = "../host/keys/user_private_key.der"

with open(private_key_path, "rb") as f:
    private_key = f.read()

signing_key = SigningKey.from_der(private_key)
verifying_key = signing_key.get_verifying_key()

player_actions = {
    "create_user": {
        "input": {},
        "default": [
            ("public_key", b64encode(verifying_key.to_der()).decode())
        ],
        "signature": [],
        "output": [
            "public_key"
        ],
    },
    "optimal_stopping_player_action": {
        "input": {
            "game_id": int,
            "game_revision": int,
            "game_action_number": int,
            "action": str
        },
        "default": [
            ("user_id", user_id),
            ("action_number", lambda: action_number),
            ("game_name", "optimal stopping")
        ],
        "signature": [
            "user_id",
            "action_number",
            "game_name",
            "game_id",
            "game_revision",
            "game_action_number",
            "action"
        ],
        "output": [
            "user_id",
            "game_id",
            "action",
            "user_signature"
        ]
    }
}

user_actions = {
    "update_host": {
        "input": {
            "id": int,
            "domain": str,
            "active": bool
        },
        "default": [
            ("user_id", user_id),
            ("action_number", lambda: action_number)
        ],
        "signature": [
            "id",
            "user_id",
            "action_number",
            "domain",
            "active"
        ],
        "output": [
            "id",
            "domain",
            "active",
            "user_signature"
        ]
    },
    "create_optimal_stopping_game": {
        "input": {
            "bet": int,
            "duration": int,
            "active": bool,
            "numbers_count": int,
            "mean": int,
            "std": int,
            "top": int,
        },
        "default": [
            ("id", None),
            ("user_id", user_id),
            ("action_number", lambda: action_number),
            ("game_name", "optimal stopping"),
            ("seed", generate_seed),
            ("seed_hash", get_seed_hash, ["seed"])
        ],
        "signature": [
            "id",
            "user_id",
            "action_number",
            "game_name",
            "bet",
            "duration",
            "active",
            "seed_hash",
            ("seed", None),
            "numbers_count",
            "mean",
            "std",
            "top"
        ],
        "output": [
            "user_id",
            "bet",
            "duration",
            "active",
            "seed",
            "numbers_count",
            "mean",
            "std",
            "top",
            "user_signature"
        ]
    },
    "update_optimal_stopping_game": {
        "input": {
            "id": int,
            "bet": int,
            "duration": int,
            "active": bool,
            "numbers_count": int,
            "mean": int,
            "std": int,
            "top": int,
        },
        "default": [
            ("user_id", user_id),
            ("action_number", lambda: action_number),
            ("game_name", "optimal stopping"),
            ("seed", generate_seed),
            ("seed_hash", get_seed_hash, ["seed"])
        ],
        "signature": [
            "id",
            "user_id",
            "action_number",
            "game_name",
            "bet",
            "duration",
            "active",
            "seed_hash",
            ("seed", None),
            "numbers_count",
            "mean",
            "std",
            "top"
        ],
        "output": [
            "id",
            "bet",
            "duration",
            "active",
            "seed",
            "numbers_count",
            "mean",
            "std",
            "top",
            "user_signature"
        ]
    }
}

if who == "player":
    actions = player_actions
else:
    actions = user_actions


while True:
    def clear_screen():
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")

    clear_screen()
    for action in actions:
        print(action)
    print("exit")
    
    action = input(">")
    clear_screen()
    
    if action == "exit":
        break

    params = {}
    for param, _type in actions[action]["input"].items():
        if _type is str:
            params[param] = input(f"{param}:{_type.__name__}>")
        elif _type is int:
            params[param] = int(input(f"{param}:{_type.__name__}>"))
        elif _type is bool:
            params[param] = input(f"{param}:{_type.__name__}>") == "t"

    clear_screen()

    for elem in actions[action]["default"]:
        if len(elem) == 2:
            param, val = elem
            if callable(val):
                params[param] = val()
            else:
                params[param] = val
        elif len(elem) == 3:
            param, f, kws = elem
            kwargs = {kw: params[kw] for kw in kws}
            params[param] = f(**kwargs)


    signature_params = {}
    for elem in actions[action]["signature"]:
        if isinstance(elem, str):
            param, val = elem, params[elem]
        elif isinstance(elem, tuple):
            param, val = elem

        signature_params[param] = val

    params["user_signature"] = sign(signature_params)

    output_params = {param: params[param] for param in actions[action]["output"]}

    action_number += 1

    print(json.dumps(output_params))
    input()
