from time import time

import requests
from flask import request

from app import app, db
from config import logger, VerificationError, HOST_ENDPOINT
from models import User, Host, game_models, game_action_models
from decorators import format_response
from formatters import format_errors, format_payload, format_data
from payload_structures import game_action_structures, reveal_setup_structure


@app.route("/play/<game_model_name>", methods=["POST"])
@format_response
def play(game_model_name):
    from tasks.payout import payout
    from tasks.complete_game_on_timeout import complete_game_on_timeout
    # player part
    game_model = game_models.get(game_model_name)
    if not game_model:
        return format_errors(["Model does not exist"], 400)

    player_payload = request.json
    structure = game_action_structures[game_model_name]["player_action"]
    formatted_player_payload, errors = format_payload(player_payload, structure)
    if errors:
        return format_errors(errors, 400)

    player = db.session.query(User).with_for_update().filter_by(id=formatted_player_payload["user_id"]).first()
    if not player:
        return format_errors(["User not found"], 404)

    player.action_number += 1

    game = db.session.query(game_model).with_for_update().filter_by(id=formatted_player_payload["game_id"]).first()
    if not game:
        return format_errors(["Game not found"], 404)

    game.actions_count += 1

    player_action_model = game_action_models[game_model_name]["player_action"]
    player_action = player_action_model(
        **formatted_player_payload,
        action_number=player.action_number,
        created_at=int(time())
    )

    errors, status_code = player_action.verify()
    if errors:
        return format_errors(errors, status_code)

    player_action.update_related()

    db.session.add(player_action)
    # host part
    def force_game_complete(errors, host_payload=None):
        logger.critical(errors, extra={"player_payload": player_payload, "host_payload": host_payload})

        game.winner_id = player.id
        payout.delay(game_model.__module__, game_model.__name__, game.id)

        db.session.commit()

    user = db.session.get(User, game.user_id)
    host = db.session.query(Host).filter_by(user_id=game.user_id).first()

    for_host_data = player_action.for_host_data
    formatted_for_host_data = format_data(for_host_data)
    try:
        endpoint = HOST_ENDPOINT.format(domain=host.domain, path=f"play/{game_model_name}")
        host_request = requests.post(endpoint, json=formatted_for_host_data)
    except requests.exceptions.RequestException as e:
        force_game_complete([str(e)])
        return game.data, 200

    try:
        host_payload = host_request.json()
    except requests.JSONDecodeError as e:
        force_game_complete([str(e)])
        return game.data, 200

    if player_action.is_last_action():
        structure = reveal_setup_structure
        formatted_host_payload, errors = format_payload(host_payload, structure)
        if errors:
            force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        game.update(**formatted_host_payload)
        try:
            game.verify_user_signature()
        except VerificationError as e:
            force_game_complete([str(e)], host_payload=host_payload)
            return game.data, 200

        game.complete()

        payout.delay(game_model.__module__, game_model.__name__, game.id)

        db.session.commit()

        return game.data, 200
    else:
        if player_action.is_first_action():
            complete_game_on_timeout.apply_async(args=[game_model.__module__, game_model.__name__, game.id], countdown=game.duration)

        structure = game_action_structures[game_model_name]["host_action"]
        formatted_host_payload, errors = format_payload(host_payload, structure)
        if errors:
            force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        host_action_model = game_action_models[game_model_name]["host_action"]
        host_action = host_action_model(
            **formatted_host_payload,
            user_id=user.id,
            action_number=user.action_number,
            game_id=game.id,
            created_at=int(time())
        )

        errors, status_code = host_action.verify()
        if errors:
            force_game_complete(errors, host_payload=host_payload)
            return game.data, 200

        db.session.add(host_action)
        db.session.commit()

        return host_action.for_player_data, 200
