from app import app, db
from models import game_models
from decorators import format_response
from formatters import format_errors


@app.route("/games/<game_name>/<id>", methods=["GET"])
@format_response
def get_game(game_name: str, id: int) -> tuple[dict, int]:
    if game_name not in game_models:
        return format_errors(["Game does not exist"], 400)

    game_model = game_models[game_name]
    game = db.session.get(game_model, id)
    if not game:
        return format_errors(["Game not found"], 404)

    return game.data, 200
