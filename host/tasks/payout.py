from sqlalchemy.exc import OperationalError

from app import app, db
from celery_app import celery_app
from models import User, game_models


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def payout(game_name: str, game_id: int) -> None:
    with app.app_context():
        user = db.session.query(User).with_for_update().first()
        game_model = game_models[game_name]
        game = db.session.query(game_model).with_for_update(nowait=True).filter_by(id=game_id).first()
        if game.paid_out:
            return

        game.paid_out = True
        user.balance += 2 * game.bet

        db.session.commit()
