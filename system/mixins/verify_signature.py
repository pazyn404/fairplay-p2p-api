import json

from app import db
from config import VerifyingKey
from formatters import format_data


class VerifySignatureMixin:
    def verify_user_signature(self):
        from models import User

        user = db.session.get(User, self.user_id)

        data = self.user_signature_data
        formatted_data = format_data(data)
        message = json.dumps(formatted_data, separators=(",", ":"))

        user_verifying_key = VerifyingKey(user.public_key)
        user_verifying_key.verify(message.encode(), self.user_signature)
