from importlib import import_module

from sqlalchemy.exc import OperationalError

from app import app, db
from celery_app import celery_app
from models import User


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def payout(game_module_name, game_model_name, game_id):
    with app.app_context():
        game_model = getattr(import_module(game_module_name), game_model_name)
        game = db.session.query(game_model).with_for_update(nowait=True).filter_by(id=game_id).first()
        if game.paid_out or game.winner_id is None:
            return

        game.paid_out = True

        winner = db.session.query(User).with_for_update().filter_by(id=game.winner_id).first()
        winner.balance += 2 * game.bet

        db.session.commit()
