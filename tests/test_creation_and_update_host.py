import json
from uuid import uuid4
from base64 import b64encode, b64decode

import requests
from ecdsa import SigningKey


def format_message(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":")).encode()


def test_creation_and_update_host(system_endpoint, system_verifying_key):
    # create user
    user_signing_key = SigningKey.generate()
    user_public_key = user_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(user_public_key).decode()
        }
    )
    payload = response.json()
    user_id = payload["id"]
    # create host
    domain = str(uuid4())
    response = requests.post(
        system_endpoint.format(path="hosts"), json={
            "user_id": user_id,
            "domain": domain,
            "active": True,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({
                    "id": None,
                    "user_id": user_id,
                    "action_number": 1,
                    "domain": domain,
                    "active": True
                }))
            ).decode()
        }
    )
    payload = response.json()
    host_id = payload["id"]
    assert response.status_code == 201
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": host_id,
            "user_id": user_id,
            "action_number": 1,
            "domain": domain,
            "active": True,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"]
        })
    )
    # update host(try to set new domain while it's active)
    new_domain = f"{domain}new"
    response = requests.put(
        system_endpoint.format(path="hosts"), json={
            "id": host_id,
            "domain": new_domain,
            "active": True,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({
                    "id": host_id,
                    "user_id": user_id,
                    "action_number": 2,
                    "domain": new_domain,
                    "active": True
                }))
            ).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 409
    assert payload == {"detail": ["Host must be turned off to change domain"]}
    # update host(on -> off with new domain)
    response = requests.put(
        system_endpoint.format(path="hosts"), json={
            "id": host_id,
            "domain": new_domain,
            "active": False,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({
                    "id": host_id,
                    "user_id": user_id,
                    "action_number": 2,
                    "domain": new_domain,
                    "active": False
                }))
            ).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 200
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": host_id,
            "user_id": user_id,
            "action_number": 2,
            "domain": new_domain,
            "active": False,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"]
        })
    )
    # update host (off -> on with new domain)
    new_new_domain = f"{new_domain}new"
    response = requests.patch(
        system_endpoint.format(path="hosts"), json={
            "id": host_id,
            "domain": new_new_domain,
            "active": True,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({
                    "id": host_id,
                    "user_id": user_id,
                    "action_number": 3,
                    "domain": new_new_domain,
                    "active": True
                }))
            ).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 200
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": host_id,
            "user_id": user_id,
            "action_number": 3,
            "domain": new_new_domain,
            "active": True,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"]
        })
    )
    # update host using put method
    response = requests.put(
        system_endpoint.format(path="hosts"), json={
            "id": host_id,
            "active": False,
            "domain": new_new_domain,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({
                    "id": host_id,
                    "user_id": user_id,
                    "action_number": 4,
                    "domain": new_new_domain,
                    "active": False
                }))
            ).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 200
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": host_id,
            "user_id": user_id,
            "action_number": 4,
            "domain": new_new_domain,
            "active": False,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"]
        })
    )
    # test signature verification
    response = requests.patch(
        system_endpoint.format(path="hosts"), json={
            "id": host_id,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({})
            )).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 401
    assert payload == {"detail": ["Invalid signature"]}
