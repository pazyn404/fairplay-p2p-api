import os

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import AppConfig, USER_VERIFYING_KEY, SYSTEM_ENDPOINT
from formatters import format_payload, format_data
from payload_structures.system import (
    create_user_structure as system_create_user_structure,
    create_host_structure as system_create_host_structure
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

        user = User(last_timestamp=formatted_payload["created_at"], **data, **formatted_payload)

        db.session.add(user)
        db.session.flush()

        errors = user.verify()
        if errors:
            raise Exception([str(error) for error in errors])

        db.session.commit()

    host = db.session.query(Host).first()
    if not host:
        signature_data = {
            "id": None, "user_id": user.id, "action_number": user.action_number + 1,
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

        formatted_payload, errors = format_payload(payload, system_create_host_structure, strict=False)
        if errors:
            raise Exception(errors)

        data.pop("user_signature")

        host = Host(action_number=user.action_number, **data, **formatted_payload)

        db.session.add(host)
        db.session.flush()

        host.update_related()
        host.fill_from_related()

        errors = host.verify()
        if errors:
            raise Exception([str(error) for error in errors])

        db.session.commit()


app = Flask(__name__)
app.config.from_object(AppConfig)

db = SQLAlchemy(app)

with app.app_context():
    from models import *
    db.create_all()
    init_host()

import endpoints
import hooks
