import os

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import AppConfig, USER_VERIFYING_KEY, SYSTEM_ENDPOINT
from formatters import format_payload, format_data
from payload_structures import (
    system_create_user_structure,
    system_create_general_structure,
    system_update_general_structure
)
from utils import sign


def init_host():
    user = db.session.query(User).first()
    if not user:
        data = {"public_key": USER_VERIFYING_KEY.key}
        formatted_data = format_data(data)

        endpoint = SYSTEM_ENDPOINT.format(path="users")
        system_request = requests.post(endpoint, json=formatted_data)

        payload = system_request.json()
        if "errors" in payload:
            raise Exception(payload["errors"])

        formatted_payload, errors = format_payload(payload, system_create_user_structure, strict=False)

        if errors:
            raise Exception(errors)

        user = User(**data, **formatted_payload, last_timestamp=formatted_payload["created_at"])

        db.session.add(user)
        db.session.flush()

        errors, status_code = user.verify()
        if errors:
            raise Exception(errors, status_code)

        db.session.commit()

    host = db.session.query(Host).first()
    if not host:
        user.action_number += 1

        signature_data = {
            "id": None, "user_id": user.id, "action_number": user.action_number,
            "domain": os.environ["HOST_DOMAIN"], "active": True
        }
        data = {
            "user_id": user.id, "domain": os.environ["HOST_DOMAIN"],
            "active": True, "user_signature": sign(signature_data)
        }

        formatted_data = format_data(data)

        endpoint = SYSTEM_ENDPOINT.format(path="hosts")
        system_request = requests.post(endpoint, json=formatted_data)

        payload = system_request.json()
        if "errors" in payload:
            raise Exception(payload["errors"])

        formatted_payload, errors = format_payload(payload, system_create_general_structure, strict=False)
        if errors:
            raise Exception(errors)

        data.pop("user_signature")

        host = Host(**data, **formatted_payload, action_number=user.action_number)

        db.session.add(host)
        db.session.flush()

        errors, status_code = host.verify()
        if errors:
            raise Exception(errors, status_code)

        user.last_timestamp = host.created_at

        db.session.commit()

    if host.domain != os.environ["HOST_DOMAIN"]:
        user.action_number += 1

        signature_data = {
            "id": host.id, "user_id": user.id, "action_number": user.action_number,
            "domain": os.environ["HOST_DOMAIN"], "active": True
        }
        data = {
            "id": host.id, "user_id": user.id, "domain": os.environ["HOST_DOMAIN"],
            "active": True, "user_signature": sign(signature_data)
        }
        formatted_data = format_data(data)

        endpoint = SYSTEM_ENDPOINT.format(path="hosts")
        system_request = requests.patch(endpoint, json=formatted_data)

        payload = system_request.json()
        if "errors" in payload:
            raise Exception(payload["errors"])

        formatted_payload, errors = format_payload(payload, system_update_general_structure, strict=False)
        if errors:
            raise Exception(errors)

        data.pop("user_signature")

        host.update(**data, **formatted_payload, action_number=user.action_number)
        errors, status_code = host.verify()
        if errors:
            raise Exception(errors, status_code)

        user.last_timestamp = host.updated_at

        db.session.commit()


app = Flask(__name__)
app.config.from_object(AppConfig)

db = SQLAlchemy(app)

with app.app_context():
    from models import *
    db.create_all()
    init_host()

import views
import hooks
