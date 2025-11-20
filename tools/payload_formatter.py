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
    private_key_path = "../host/keys/host_user_private_key.der"

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
            ("game_revision", "game.action_number(e.g. host_user.action_number what was used to lastly create or update the game"): int,
            ("game_action_number", "The  action number in the game(start from 1)"): int,
            ("action", "next or stop(stop can't be first action)"): str
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

host_user_actions = {
    "update_host": {
        "input": {
            "id": int,
            "domain": str,
            ("active", "should be 't' or 'f'"): bool
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
            ("bet", "should be grater than 0"): int,
            ("duration", "should be between 11 and 299 inclusive"): int,
            ("active", "should be 't' or 'f'(defines whether balance will be updated(withdraw money from balance if 't', leave balance unchanged if 'f'))"): bool,
            ("numbers_count", "should be between 11 and 49 inclusive"): int,
            ("mean", "should be between 1 and 999 inclusive"): int,
            ("std", "should be between 101 and 999 inclusive"): int,
            ("top", "should be between 2 and 49 inclusive"): int,
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
            ("bet", "should be grater than 0"): int,
            ("duration", "should be between 11 and 299 inclusive"): int,
            ("active", "set to 't' or 'f'(defines whether balance will be updated(t->f return money to balance, f->t withdraw money from balance))"): bool,
            ("numbers_count", "should be between 11 and 49 inclusive"): int,
            ("mean", "should be between 1 and 999 inclusive"): int,
            ("std", "should be between 101 and 999 inclusive"): int,
            ("top", "should be between 2 and 49 inclusive"): int,
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

if who == "host_user":
    actions = host_user_actions
elif who == "player":
    actions = player_actions
else:
    raise Exception("Unknown role(choose between host and player)")

actions_list = list([*actions.keys(), "exit"])

while True:
    def clear_screen() -> None:
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")

    def safe_input(prompt, _type: type[int, str, bool]) -> int | str | bool:
        while True:
            value = input(prompt)
            try:
                if _type is int:
                    return int(value)
                if _type is bool:
                    if value not in ("t", "f"):
                        raise ValueError
                    return value == "t"
                return value
            except ValueError:
                pass

    clear_screen()
    for i, action in enumerate(actions_list):
        print(f"{i + 1}: {action}")
    
    number = safe_input("number>", int) - 1
    clear_screen()

    if not 0 <= number < len(actions_list):
        continue

    action = actions_list[number]

    if action == "exit":
        break

    params = {}
    for param, _type in actions[action]["input"].items():
        if isinstance(param, tuple):
            param_name, param_description = param
        else:
            param_name, param_description = param, ""
        prompt = f"{param_name}({param_description}):{_type.__name__}>"
        params[param_name] = safe_input(prompt, _type)

    clear_screen()

    for elem in actions[action]["default"]:
        if len(elem) == 2:
            param_name, val = elem
            if callable(val):
                params[param_name] = val()
            else:
                params[param_name] = val
        elif len(elem) == 3:
            param_name, f, kws = elem
            kwargs = {kw: params[kw] for kw in kws}
            params[param_name] = f(**kwargs)

    signature_params = {}
    for elem in actions[action]["signature"]:
        if isinstance(elem, str):
            param_name, val = elem, params[elem]
        elif isinstance(elem, tuple):
            param_name, val = elem

        signature_params[param_name] = val

    params["user_signature"] = sign(signature_params)

    output_params = {param_name: params[param_name] for param_name in actions[action]["output"]}

    action_number += 1

    print(json.dumps(output_params))
    input()
