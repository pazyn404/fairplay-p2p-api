import json

from config import VerifyingKey


class VerifySignatureMixin:
    def verify_user_signature(self) -> None:
        data = self.user_signature_data
        message = json.dumps(data, separators=(",", ":"))

        user_verifying_key = VerifyingKey(self.user.public_key)
        user_verifying_key.verify(message.encode(), self.user_signature)
