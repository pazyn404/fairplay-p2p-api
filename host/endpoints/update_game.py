from hashlib import sha256

import requests
from flask import request

from app import app, db
from config import SYSTEM_ENDPOINT
from models import game_models
from decorators import format_response
from formatters import (
    format_payload,
    format_errors,
    format_system_errors,
    format_system_verification_errors,
    format_data
)
from payload_structures.user import update_game_structures as user_update_game_structures
from payload_structures.system import update_game_structure as system_update_game_structure


@app.route("/games/<game_name>", methods=["PUT", "PATCH"])
@format_response
def update_game(game_name: str) -> tuple[dict, int]:
    if game_name not in game_models:
        return format_errors(["Game does not exist"], 400)

    game_model = game_models[game_name]
    user_update_game_structure = user_update_game_structures[game_name]

    user_payload = request.json
    formatted_user_payload, errors = format_payload(user_payload, user_update_game_structure, strict=False)
    if errors:
        return format_errors(errors, 400)

    if "seed" in formatted_user_payload:
        seed = formatted_user_payload["seed"]
        seed_hash = sha256(seed).digest()

        user_payload.pop("seed")
        user_payload["seed_hash"] = format_data(seed_hash)

    try:
        endpoint = SYSTEM_ENDPOINT.format(path=f"games/{game_name}")
        system_request = requests.patch(endpoint, json=user_payload)
    except requests.exceptions.ConnectionError as e:
        return format_system_errors([str(e)], 400, user_payload=user_payload)

    try:
        system_payload = system_request.json()
    except requests.exceptions.JSONDecodeError as e:
        return format_system_errors([str(e)], 415, user_payload=user_payload)

    if "errors" in system_payload:
        return format_errors(system_payload["errors"], system_request.status_code)

    formatted_system_payload, errors = format_payload(system_payload, system_update_game_structure, strict=False)
    if errors:
        return format_system_errors(errors, 400, user_payload=user_payload)

    game = db.session.get(game_model, formatted_user_payload["id"])
    if not game:
        return format_system_errors(["Game not found"], 404, user_payload=user_payload, system_payload=system_payload)

    game.store_prev_data()
    game.update(**formatted_user_payload, **formatted_system_payload)
    game.update_related()
    game.fill_from_related()

    errors = game.verify()
    if errors:
        return format_system_verification_errors(errors, user_payload=user_payload, system_payload=system_payload)

    db.session.commit()

    return {"id": game.id, "action_number": game.action_number}, 200
