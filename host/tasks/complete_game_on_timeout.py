from sqlalchemy.exc import OperationalError

from app import app, db
from celery_app import celery_app
from models import BaseGame


@celery_app.task(
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": None, "countdown": 10}
)
def complete_game_on_timeout(game_id):
    with app.app_context():
        game = db.session.query(BaseGame).with_for_update().filter_by(id=game_id).first()
        game.pending = False
        game.complete = True
        db.session.commit()
