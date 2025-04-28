from app import db
from config import VerifyingKey
from .base_model import BaseModel


class User(BaseModel):
    DATA_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "public_key", "action_number", "balance", "created_at"]

    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.LargeBinary, nullable=False)
    action_number = db.Column(db.Integer, nullable=False, default=0)
    balance = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, nullable=False)

    def verify_public_key(self):
        VerifyingKey(self.public_key)
