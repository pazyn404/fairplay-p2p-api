import requests
from flask import request

from app import app, db
from config import SYSTEM_ENDPOINT
from models import Host
from decorators import format_response
from formatters import (
    format_payload,
    format_errors,
    format_system_errors,
    format_system_verification_errors,
    format_data
)
from payload_structures.user import update_host_structure as user_update_host_structure
from payload_structures.system import update_host_structure as system_update_host_structure


@app.route("/hosts", methods=["PUT", "PATCH"])
@format_response
def update_host() -> tuple[dict, int]:
    user_payload = request.json
    formatted_user_payload, errors = format_payload(user_payload, user_update_host_structure, strict=False)
    if errors:
        return format_errors(errors, 400)

    try:
        endpoint = SYSTEM_ENDPOINT.format(path="hosts")
        system_request = requests.patch(endpoint, json=user_payload)
    except requests.exceptions.ConnectionError as e:
        return format_system_errors([str(e)], 400, user_payload=user_payload)

    try:
        system_payload = system_request.json()
    except requests.exceptions.JSONDecodeError as e:
        return format_system_errors([str(e)], 415, user_payload=user_payload)

    if "errors" in system_payload:
        return format_errors(system_payload["errors"], system_request.status_code)

    formatted_system_payload, errors = format_payload(system_payload, system_update_host_structure, strict=False)
    if errors:
        return format_system_errors(errors, 400, user_payload=user_payload)

    host = db.session.get(Host, formatted_user_payload["id"])
    if not host:
        return format_system_errors(["Host not found"], 404, user_payload=user_payload, system_payload=system_payload)

    host.update(**formatted_user_payload, **formatted_system_payload)
    host.update_related()
    host.fill_from_related()

    errors = host.verify()
    if errors:
        return format_system_verification_errors(errors, user_payload=user_payload, system_payload=system_payload)

    db.session.commit()

    return {}, 200
