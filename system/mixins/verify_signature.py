import json

from config import VerifyingKey
from formatters import format_data


class VerifySignatureMixin:
    def verify_user_signature(self):
        data = self.user_signature_data
        formatted_data = format_data(data)
        message = json.dumps(formatted_data, separators=(",", ":"))

        user_verifying_key = VerifyingKey(self.user.public_key)
        user_verifying_key.verify(message.encode(), self.user_signature)
