from base64 import b64encode

from app import app
from keys import SYSTEM_VERIFYING_KEY


@app.api_route("/system_public_key", methods=["GET"])
async def system_public_key() -> dict[str, str]:
    return {
        "system_public_key": b64encode(SYSTEM_VERIFYING_KEY.key).decode()
    }
