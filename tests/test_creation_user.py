import json
from base64 import b64encode, b64decode

import requests
from ecdsa import SigningKey


def format_message(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":")).encode()


def test_creation_user(system_endpoint, system_verifying_key):
    # send invalid public_key
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(b"invalid_key").decode()
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": ["Invalid public key"]}
    # create user
    new_user_signing_key = SigningKey.generate()
    new_user_public_key = new_user_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(new_user_public_key).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 201
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": payload["id"],
            "public_key": payload["public_key"],
            "action_number": 0,
            "balance": 0,
            "created_at": payload["created_at"]
        })
    )
