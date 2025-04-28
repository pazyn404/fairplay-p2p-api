from app import db
from .base_model import BaseModel


class User(BaseModel):
    DATA_ATTRIBUTES = ["id", "public_key", "action_number", "created_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "public_key", "action_number", ("balance", 0), "created_at"]

    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.LargeBinary, nullable=False)
    action_number = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, nullable=False)
    last_timestamp = db.Column(db.Integer, nullable=False)
    system_signature = db.Column(db.LargeBinary, nullable=False)
