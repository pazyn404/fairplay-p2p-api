import json

from config import VerifyingKey
from formatters import format_data


class VerifySignatureMixin:
    async def verify_user_signature(self):
        from models import User

        user = await self.session.get(User, self.user_id)

        data = await self.user_signature_data
        formatted_data = format_data(data)
        message = json.dumps(formatted_data, separators=(",", ":"))

        user_verifying_key = VerifyingKey(user.public_key)
        user_verifying_key.verify(message.encode(), self.user_signature)
