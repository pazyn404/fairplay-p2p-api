from time import time

from flask import request

from app import app, db
from config import inflect_engine
from models import User, Host, game_models
from decorators import format_response
from formatters import format_payload, format_errors
from payload_structures import update_structures


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

    payload = request.json
    structure = update_structures[model_name]
    formatted_payload, errors = format_payload(payload, structure)
    if errors:
        return format_errors(errors, 400)

    instance = db.session.query(model).with_for_update().filter_by(id=formatted_payload["id"]).first()
    if not instance:
        return format_errors(["Instance not found"], 404)

    user = db.session.query(User).with_for_update().filter_by(id=instance.user_id).first()
    user.action_number += 1

    instance.action_number = user.action_number
    instance.updated_at = int(time())

    prev_data = instance.curr_data
    instance.update(**formatted_payload)
    errors, status_code = instance.verify(prev_data)
    if errors:
        db.session.rollback()
        return format_errors(errors, status_code)

    instance.update_related(prev_data)

    db.session.commit()

    return instance.data, 200
