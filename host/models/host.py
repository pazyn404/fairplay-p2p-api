from app import db
from mixins import VerifyTimestampMixin
from .base_model import BaseModel


class Host(VerifyTimestampMixin, BaseModel):
    DATA_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    domain = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    action_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)
