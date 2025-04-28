from time import time

from flask import request

from app import app, db
from config import inflect_engine
from models import User, Host, game_models
from decorators import format_response
from formatters import format_payload, format_errors
from payload_structures import create_structures


models = {
    "user": User,
    "host": Host,
    **game_models
}


@app.route("/<plural_model_name>", methods=["POST"])
@format_response
def create(plural_model_name):
    model_name = inflect_engine.singular_noun(plural_model_name)
    model = models.get(model_name)
    if not model:
        return format_errors(["Model does not exist"], 400)

    payload = request.json
    structure = create_structures[model_name]
    formatted_payload, errors = format_payload(payload, structure)
    if errors:
        return format_errors(errors, 400)

    _time = int(time())
    instance = model(created_at=_time, **formatted_payload)
    if model is not User:
        user = db.session.query(User).with_for_update().filter_by(id=formatted_payload["user_id"]).first()
        if not user:
            return format_errors(["User not found"], 404)

        user.action_number += 1

        instance.action_number = user.action_number
        instance.updated_at = _time

    errors, status_code = instance.verify()
    if errors:
        db.session.rollback()
        return format_errors(errors, status_code)

    instance.update_related()

    db.session.add(instance)
    db.session.commit()

    return instance.data, 201
