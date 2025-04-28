from app import db
from mixins import HostActionMixin
from .base_game_action import BaseGameAction


class OptimalStoppingHostAction(HostActionMixin, BaseGameAction):
    DATA_ATTRIBUTES = BaseGameAction.DATA_ATTRIBUTES + ["number"]
    SYSTEM_SIGNATURE_ATTRIBUTES = BaseGameAction.SYSTEM_SIGNATURE_ATTRIBUTES + ["number"]
    USER_SIGNATURE_ATTRIBUTES = BaseGameAction.USER_SIGNATURE_ATTRIBUTES + ["number"]

    FOR_PLAYER_DATA_ATTRIBUTES = HostActionMixin.FOR_PLAYER_DATA_ATTRIBUTES + ["number"]
    FOR_PLAYER_SIGNATURE_ATTRIBUTES = HostActionMixin.FOR_PLAYER_SIGNATURE_ATTRIBUTES + ["number"]

    number = db.Column(db.Integer, nullable=False)
