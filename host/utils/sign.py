import json

from config import USER_SIGNING_KEY
from formatters import format_data


def sign(data: dict) -> bytes:
    formatted_data = format_data(data)
    message = json.dumps(formatted_data, separators=(",", ":"))
    signature = USER_SIGNING_KEY.sign(message.encode())

    return signature
