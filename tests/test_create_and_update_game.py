import json
from uuid import uuid4
from hashlib import sha256
from base64 import b64encode, b64decode

import pytest
import requests
from ecdsa import SigningKey


def format_message(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":")).encode()


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5})
])
def test_creation_game_without_host_setup(system_endpoint, system_verifying_key, game_name, game_name_url, specific_game_params):
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
    user_action_number = 0
    # create inactive game
    response = requests.post(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": user_id,
            "bet": 50,
            "duration": 60,
            "active": False,
            "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
            **specific_game_params,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": None,
                "user_id": user_id,
                "action_number": user_action_number + 1,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": False,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 409
    assert payload == {"detail": ["Host is not set up"]}


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5})
])
def test_creation_and_update_game(system_endpoint, system_verifying_key, game_name, game_name_url, specific_game_params):
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
    user_action_number = 0
    # create host
    domain = str(uuid4())
    requests.post(
        system_endpoint.format(path="hosts"), json={
            "user_id": user_id,
            "domain": domain,
            "active": True,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({
                    "id": None,
                    "user_id": user_id,
                    "action_number": user_action_number + 1,
                    "domain": domain,
                    "active": True
                }))
            ).decode(),
        }
    )
    # create inactive game
    response = requests.post(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": user_id,
            "bet": 50,
            "duration": 60,
            "active": False,
            "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
            **specific_game_params,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": None,
                "user_id": user_id,
                "action_number": user_action_number + 2,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": False,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    game_id = payload["id"]
    assert response.status_code == 201
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": game_id,
            "user_id": user_id,
            "player_id": None,
            "winner_id": None,
            "action_number": user_action_number + 2,
            "game_action_number": 0,
            "game_name": game_name,
            "bet": 50,
            "duration": 60,
            "active": False,
            "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
            "seed": None,
            "started_at": None,
            "finished_at": None,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"],
            **specific_game_params
        })
    )
    # try to activate game with insufficient balance
    response = requests.patch(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "active": True,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": user_id,
                "action_number": user_action_number + 3,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 409
    assert payload == {"detail": ["Insufficient balance"]}
    # test signature verification
    response = requests.patch(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "user_signature": b64encode(user_signing_key.sign(
                format_message({})
            )).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 401
    assert payload == {"detail": ["Invalid signature"]}
    # next few tests test balance
    def get_user_balance() -> int:
        response = requests.get(system_endpoint.format(path=f"users/{user_id}"))
        return response.json()["balance"]

    requests.post(system_endpoint.format(path=f"faucet/{user_id}"), json={})
    # inactive -> active
    response = requests.patch(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "active": True,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": user_id,
                "action_number": user_action_number + 3,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_user_balance() == 50
    # change bet
    response = requests.patch(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "bet": 40,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": user_id,
                "action_number": user_action_number + 4,
                "game_name": game_name,
                "bet": 40,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_user_balance() == 60
    # active -> inactive
    response = requests.patch(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "bet": 50,
            "active": False,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": user_id,
                "action_number": user_action_number + 5,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": False,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_user_balance() == 100
    # update game using put method
    response = requests.put(
        system_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "bet": 50,
            "duration": 60,
            "active": True,
            "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
            **specific_game_params,
            "user_signature": b64encode(user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": user_id,
                "action_number": user_action_number + 6,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 200
    assert get_user_balance() == 50
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": game_id,
            "user_id": user_id,
            "player_id": None,
            "winner_id": None,
            "action_number": user_action_number + 6,
            "game_action_number": 0,
            "game_name": game_name,
            "bet": 50,
            "duration": 60,
            "active": True,
            "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
            "seed": None,
            "started_at": None,
            "finished_at": None,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"],
            **specific_game_params
        })
    )


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5})
])
def test_creation_and_update_game_via_host(
        system_endpoint, host_endpoint, host_user_signing_key, system_verifying_key, game_name, game_name_url, specific_game_params
):
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
    host_user_balance = payload["balance"]

    # create inactive game
    response = requests.post(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": host_user_id,
            "bet": 50,
            "duration": 60,
            "active": False,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": None,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 1,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": False,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    game_id = payload["id"]
    assert response.status_code == 201
    # verify system signature
    response = requests.get(host_endpoint.format(path=f"games/{game_name_url}/{game_id}"))
    payload = response.json()
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "id": game_id,
            "user_id": host_user_id,
            "player_id": None,
            "winner_id": None,
            "action_number": host_user_action_number + 1,
            "game_action_number": 0,
            "game_name": game_name,
            "bet": 50,
            "duration": 60,
            "active": False,
            "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
            "seed": None,
            "started_at": None,
            "finished_at": None,
            "created_at": payload["created_at"],
            "updated_at": payload["updated_at"],
            **specific_game_params
        })
    )
    # next few tests test balance
    def get_host_user_balance() -> int:
        response = requests.get(host_endpoint.format(path="users"))
        return response.json()["balance"] - host_user_balance

    requests.post(system_endpoint.format(path=f"faucet/{host_user_id}"), json={})
    requests.post(host_endpoint.format(path="faucet"), json={})
    # inactive -> active
    response = requests.patch(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "active": True,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 2,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_host_user_balance() == 50
    # change bet
    response = requests.patch(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "bet": 40,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 3,
                "game_name": game_name,
                "bet": 40,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_host_user_balance() == 60
    # active -> inactive
    response = requests.patch(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "bet": 50,
            "active": False,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 4,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": False,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_host_user_balance() == 100
    # update game using put method
    response = requests.put(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "id": game_id,
            "bet": 50,
            "duration": 60,
            "active": True,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": game_id,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 5,
                "game_name": game_name,
                "bet": 50,
                "duration": 60,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    assert response.status_code == 200
    assert get_host_user_balance() == 50
