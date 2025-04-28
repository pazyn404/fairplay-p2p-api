from app import db
from config import VerificationError
from mixins import VerifySignatureMixin
from .base_model import BaseModel


class Host(VerifySignatureMixin, BaseModel):
    DATA_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at", "system_signature"]
    SYSTEM_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active", "created_at", "updated_at"]
    USER_SIGNATURE_ATTRIBUTES = ["id", "user_id", "action_number", "domain", "active"]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    domain = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    action_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    user_signature = db.Column(db.LargeBinary, nullable=False)

    def verify_turn_off(self):
        from .base_game import BaseGame

        if self.active:
           return

        for game_model in BaseGame.__subclasses__():
            if db.session.query(game_model).filter(game_model.user_id == self.user_id, game_model.active == True, game_model.winner_id.is_(None)).all():
                raise VerificationError("Host can't be turned off during active or pending games", 409)

    def verify_domain_change(self, prev_domain, prev_active):
        if not prev_domain or not self.active or not prev_active:
            return

        if self.domain != prev_domain:
            raise VerificationError("Host must be turned off to change domain", 409)

    def verify_unique(self):
        host = db.session.query(Host).filter_by(user_id=self.user_id).first()

        if host and self.id != host.id:
            raise VerificationError("Host already exists", 409)
