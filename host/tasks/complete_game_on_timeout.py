from sqlalchemy.exc import OperationalError

from app import app, db
from celery_app import celery_app
from models import game_models
from .payout import payout


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def complete_game_on_timeout(game_name: str, game_id: int) -> None:
    with app.app_context():
        game_model = game_models[game_name]
        game = db.session.query(game_model).with_for_update().filter_by(id=game_id).first()
        if game.pending:
            game.pending = False
            game.completed = True
            game.win = True

            payout.delay(game_name, game_id)

            db.session.commit()
