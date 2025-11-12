import json

from fastapi import Request
from starlette.responses import JSONResponse

from app import app


@app.middleware("http")
async def verify_payload(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH") and request.headers.get("Content-Type") != "application/json":
        return JSONResponse({"detail": ["Content-Type must be application/json"]}, 415)

    if request.headers.get("Content-Type") == "application/json":
        try:
            await request.json()
        except json.decoder.JSONDecodeError:
            return JSONResponse({"detail": ["Malformed payload"]}, 400)

    return await call_next(request)
