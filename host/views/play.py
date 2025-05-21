from flask import request

from app import app, db
from models import BaseGame, game_system_action_models, User
from decorators import format_response
from formatters import format_system_errors, format_payload
from payload_structures import system_game_action_structures


@app.route("/play/<game_model_name>", methods=["POST"])
@format_response
def play(game_model_name):
    from tasks.complete_game_on_timeout import complete_game_on_timeout

    system_payload = request.json

    if game_model_name not in system_game_action_structures:
        return format_system_errors(["Game model does not exist"], 400, system_payload=system_payload)

    structure = system_game_action_structures[game_model_name]
    formatted_system_payload, errors = format_payload(system_payload, structure)
    if errors:
        return format_system_errors(errors, 400, system_payload=system_payload)

    user = db.session.query(User).first()
    game = db.session.get(BaseGame, formatted_system_payload["game_id"])

    game_system_action_model = game_system_action_models[game_model_name]
    system_action = game_system_action_model(
        **formatted_system_payload,
        user_id=user.id,
        action_number=user.action_number,
        game_action_number=game.actions_count + 1
    )

    db.session.add(system_action)
    db.session.flush()

    system_action.update_related()
    errors, status_code = system_action.verify()
    if errors:
        db.session.rollback()
        return format_system_errors(errors, 400, system_payload=system_payload)

    db.session.commit()

    if system_action.is_first_action():
        complete_game_on_timeout.apply_async(args=[game.id], countdown=game.duration)

    if system_action.is_last_action():
        return game.revealed_data, 200
    else:
        return system_action.for_system_data, 200
