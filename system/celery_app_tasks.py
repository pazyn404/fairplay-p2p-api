from sqlalchemy.exc import OperationalError

from celery_app import celery_app
from celery_app_db import get_session
from models import UserModel, game_models


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def complete_game_on_timeout(game_name: str, game_id: int) -> None:
    with get_session() as session:
        game_model = game_models[game_name]
        game = session.query(game_model).with_for_update(nowait=True).filter_by(id=game_id).first()
        if game.winner_id is None:
            game.winner_id = game.user_id
            game.finished_at = game.started_at + game.duration

            payout.delay(game_name, game_id)

            session.commit()


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def payout(game_name: str, game_id: int) -> None:
    with get_session() as session:
        game_model = game_models[game_name]
        game = session.query(game_model).with_for_update(nowait=True).filter_by(id=game_id).first()
        if game.paid_out or game.winner_id is None:
            return

        game.paid_out = True

        winner = session.query(UserModel).with_for_update().filter_by(id=game.winner_id).first()
        winner.balance += 2 * game.bet

        session.commit()
