from flask import request

from app import app, db
from models import game_models, game_action_models, User
from decorators import format_response
from formatters import format_system_errors, format_payload
from payload_structures import system_game_action_structures


@app.route("/play/<game_model_name>", methods=["POST"])
@format_response
def play(game_model_name):
    system_payload = request.json

    game_model = game_models.get(game_model_name)
    if not game_model:
        return format_system_errors(["Game model does not exist"], 400, system_payload=system_payload)

    structure = system_game_action_structures[game_model_name]
    formatted_system_payload, errors = format_payload(system_payload, structure)
    if errors:
        return format_system_errors(errors, 400, system_payload=system_payload)

    game = db.session.get(game_model, formatted_system_payload["game_id"])
    game.actions_count += 1

    user = db.session.query(User).first()

    game_system_action_model = game_action_models[game_model_name]
    system_action = game_system_action_model(
        **formatted_system_payload,
        user_id=user.id,
        action_number=user.action_number
    )
    errors, status_code = system_action.verify()
    if errors:
        return format_system_errors(errors, 400, system_payload=system_payload)

    system_action.update_related()

    db.session.add(system_action)
    db.session.commit()

    if system_action.is_last_action():
        return game.revealed_data, 200
    else:
        return system_action.for_system_data, 200
