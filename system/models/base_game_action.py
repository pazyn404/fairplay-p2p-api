from app import db
from mixins import VerifySignatureMixin
from .base_model import BaseModel
from ._abstract_mapping import mapping


class BaseGameAction(VerifySignatureMixin, BaseModel):
    __abstract__ = True

    DATA_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id",
        "game_revision|{GAME_MODEL}:game_id.action_number","created_at", "system_signature"
    ]
    SYSTEM_SIGNATURE_ATTRIBUTES = [
        "id", "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id",
        "game_revision|{GAME_MODEL}:game_id.action_number", "created_at"
    ]
    USER_SIGNATURE_ATTRIBUTES = [
        "user_id", "action_number", "game_name|{GAME_MODEL}.GAME_NAME", "game_id",
        "game_revision|{GAME_MODEL}:game_id.action_number", "game_action_number|{GAME_MODEL}:game_id.actions_count"
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    action_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    user_signature = db.Column(db.LargeBinary, nullable=False)

    def __init_subclass__(cls, **kwargs):
        game_model_table_name = mapping[cls.__name__]["game_id"]
        cls.game_id = db.Column(db.Integer, db.ForeignKey(f"{game_model_table_name}.id"), nullable=False, index=True)
