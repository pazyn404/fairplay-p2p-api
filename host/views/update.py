from hashlib import sha256

import requests
from flask import request

from app import app, db
from config import inflect_engine, SYSTEM_ENDPOINT
from models import game_models, User, Host
from decorators import format_response
from formatters import format_payload, format_errors, format_system_errors, format_data
from payload_structures import user_update_structures, system_update_general_structure


models = {
    "host": Host,
    **game_models
}


@app.route("/<plural_model_name>", methods=["PUT", "PATCH"])
@format_response
def update(plural_model_name):
    model_name = inflect_engine.singular_noun(plural_model_name)
    model = models.get(model_name)
    if not model:
        return format_errors(["Model does not exist"], 400)

    user = db.session.query(User).with_for_update().first()
    user.action_number += 1

    user_payload = request.json
    user_structure = user_update_structures[model_name]
    formatted_user_payload, errors = format_payload(user_payload, user_structure, strict=False)
    if errors:
        return format_errors(errors, 400)

    if "seed" in formatted_user_payload:
        seed = formatted_user_payload["seed"]
        seed_hash = sha256(seed).digest()

        user_payload.pop("seed")
        user_payload["seed_hash"] = format_data(seed_hash)

    try:
        endpoint = SYSTEM_ENDPOINT.format(path=plural_model_name)
        system_request = requests.patch(endpoint, json=user_payload)
    except requests.exceptions.ConnectionError as e:
        return format_system_errors([str(e)], 400, user_payload=user_payload)

    try:
        system_payload = system_request.json()
    except requests.exceptions.JSONDecodeError as e:
        return format_system_errors([str(e)], 415, user_payload=user_payload)

    if "errors" in system_payload:
        return format_errors(system_payload["errors"], system_request.status_code)

    formatted_system_payload, errors = format_payload(system_payload, system_update_general_structure, strict=False)
    if errors:
        return format_system_errors(errors, 400, user_payload=user_payload)

    instance = db.session.get(model, formatted_user_payload["id"])
    if not instance:
        return format_system_errors(["Instance not found"], 404, user_payload=user_payload, system_payload=system_payload)

    prev_data = instance.__dict__.copy()
    instance.update(**formatted_user_payload, **formatted_system_payload, action_number=user.action_number)
    errors, status_code = instance.verify(prev_data)
    if errors:
        return format_system_errors(errors, status_code, user_payload=user_payload, system_payload=system_payload)

    user.last_timestamp = instance.updated_at

    db.session.commit()

    return {}, 200
