from flask import request

from app import app


@app.before_request
def before_request() -> tuple[dict[str, list[str]], int] | None:
    if request.method == "GET":
        return
    if request.headers.get("Content-Type") != "application/json":
        return {
            "errors": [
                "Content-Type must be application/json"
            ]
        }, 415
