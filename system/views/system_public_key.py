from app import app
from config import SYSTEM_VERIFYING_KEY
from decorators import format_response


@app.api_route("/system_public_key", methods=["GET"])
@format_response
async def system_public_key():
    return {"system_public_key": SYSTEM_VERIFYING_KEY.key}, 200
