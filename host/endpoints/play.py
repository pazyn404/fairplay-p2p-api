from flask import request

from app import app, db
from models import User, game_models, game_system_action_models
from decorators import format_response
from formatters import (
    format_payload,
    format_system_errors,
    format_system_verification_errors
)
from payload_structures.system import game_system_action_structures


@app.route("/play/<game_name>", methods=["POST"])
@format_response
def play(game_name: str) -> tuple[dict, int]:
    from tasks.complete_game_on_timeout import complete_game_on_timeout
    from tasks.payout import payout

    game_model = game_models[game_name]
    system_action_model = game_system_action_models[game_name]

    system_action_structure = game_system_action_structures[game_name]

    system_payload = request.json
    if game_name not in game_models:
        return format_system_errors(["Game does not exist"], 400, system_payload=system_payload)

    formatted_system_payload, errors = format_payload(system_payload, system_action_structure)
    if errors:
        return format_system_errors(errors, 400, system_payload=system_payload)

    user = db.session.query(User).first()
    game = db.session.query(game_model).with_for_update().filter_by(id=formatted_system_payload["game_id"]).first()
    system_action = system_action_model(
        user_id=user.id,
        action_number=-1,
        game_action_number=-1,
        **formatted_system_payload
    )

    db.session.add(system_action)
    db.session.flush()

    system_action.update_related()
    system_action.fill_from_related()

    errors = system_action.verify()
    if errors:
        return format_system_verification_errors(errors, system_payload=system_payload)

    if system_action.is_first_action():
        complete_game_on_timeout.apply_async(args=[game_name, game.id], countdown=game.duration)

    if system_action.is_last_action():
        game.complete()

        db.session.commit()

        if game.win:
            payout.delay(game_name, game.id)

        return game.revealed_data, 200
    else:
        db.session.commit()
        return system_action.for_system_data, 200
