import json

from keys import SYSTEM_SIGNING_KEY


def sign(data: dict[str, int | str | None]) -> bytes:
    message = json.dumps(data, separators=(",", ":"))
    signature = SYSTEM_SIGNING_KEY.sign(message.encode())

    return signature
