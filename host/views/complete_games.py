from sqlalchemy.orm import selectinload

from app import app, db
from config import inflect_engine
from models import Host, game_models
from decorators import format_response
from formatters import format_errors


@app.route("/<plural_game_model_name>/complete", methods=["GET"])
@format_response
def complete_games(plural_game_model_name):
    game_model_name = inflect_engine.singular_noun(plural_game_model_name)
    game_model = game_models.get(game_model_name)
    if not game_model:
        return format_errors(["Model does not exist"], 400)

    games = db.session.query(game_model).join(Host, game_model.user_id == Host.user_id).filter(
        game_model.complete == True
    ).options(selectinload(game_model.system_actions)).all()
    return {"games": [game.data for game in games]}, 200
