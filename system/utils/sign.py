import json

from config import SYSTEM_SIGNING_KEY
from formatters import format_data


def sign(data):
    formatted_data = format_data(data)
    message = json.dumps(formatted_data, separators=(",", ":"))
    signature = SYSTEM_SIGNING_KEY.sign(message.encode())

    return signature
