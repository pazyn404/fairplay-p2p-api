from app import db
from .base_game import BaseGame


class OptimalStoppingGame(BaseGame):
    __mapper_args__ = {
        "polymorphic_identity": "optimal_stopping_game",
        "polymorphic_load": "selectin"
    }

    GAME_NAME = "optimal stopping"

    DATA_ATTRIBUTES = BaseGame.DATA_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGame.SYSTEM_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    REVEALED_SIGNATURE_ATTRIBUTES = BaseGame.REVEALED_SIGNATURE_ATTRIBUTES + ["numbers_count", "mean", "std", "top"]

    numbers_count = db.Column(db.Integer, nullable=False)
    mean = db.Column(db.Integer, nullable=False)
    std = db.Column(db.Integer, nullable=False)
    top = db.Column(db.Integer, nullable=False)
