from importlib import import_module

from sqlalchemy.exc import OperationalError

from app import app
from db import get_sync_session
from celery_app import celery_app
from .payout import payout


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def complete_game_on_timeout(game_module_name, game_model_name, game_id):
    session = get_sync_session()

    game_model = getattr(import_module(game_module_name), game_model_name)
    game = session.query(game_model).with_for_update(nowait=True).filter_by(id=game_id).first()
    if game.winner_id is None:
        game.winner_id = game.user_id
        game.finished_at = game.started_at + game.duration

        payout.delay(game_module_name, game_model_name, game_id)

        session.commit()
