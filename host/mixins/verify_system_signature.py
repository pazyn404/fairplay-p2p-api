import json

from config import SYSTEM_VERIFYING_KEY
from formatters import format_data


class VerifySystemSignatureMixin:
    def verify_system_signature(self):
        data = self.system_signature_data
        formatted_data = format_data(data)
        message = json.dumps(formatted_data, separators=(",", ":"))

        SYSTEM_VERIFYING_KEY.verify(message.encode(), self.system_signature)
