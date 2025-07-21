from sqlalchemy.orm import selectinload

from app import app, db
from models import Host, game_models
from decorators import format_response
from formatters import format_errors


@app.route("/games/<game_name>/available", methods=["GET"])
@format_response
def available_games(game_name: str) -> tuple[dict, int]:
    game_model = game_models.get(game_name)
    if not game_model:
        return format_errors(["Game does not exist"], 400)

    games = (db.session.query(game_model).filter_by(active=True, pending=False, completed=False).
             options(selectinload(game_model.system_actions)).all())
    return {"games": [game.data for game in games]}, 200
