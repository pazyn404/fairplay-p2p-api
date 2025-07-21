from sqlalchemy.exc import OperationalError

from app import app
from db import get_sync_session
from celery_app import celery_app
from models import UserModel, game_models


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def payout(game_name: str, game_id: int) -> None:
    session = get_sync_session()
    game_model = game_models[game_name]
    game = session.query(game_model).with_for_update(nowait=True).filter_by(id=game_id).first()
    if game.paid_out or game.winner_id is None:
        return

    game.paid_out = True

    winner = session.query(UserModel).with_for_update().filter_by(id=game.winner_id).first()
    winner.balance += 2 * game.bet

    session.commit()
