import time
import json
from hashlib import sha256
from base64 import b64encode, b64decode

import pytest
import requests
from ecdsa import SigningKey


def format_message(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":")).encode()


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params, specific_game_player_action_params", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5}, {"action": "next"})
])
def test_play_inactive_game(
    system_endpoint,
    host_endpoint,
    host_user_signing_key,
    game_name,
    game_name_url,
    specific_game_params,
    specific_game_player_action_params
):
    # create player
    player_signing_key = SigningKey.generate()
    player_public_key = player_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(player_public_key).decode()
        }
    )
    payload = response.json()
    player_id = payload["id"]
    player_action_number = 0

    requests.post(system_endpoint.format(path=f"faucet/{player_id}"), json={})
    # get host_user data
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
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
    game_revision = payload["action_number"]
    # try to start inactive game
    response = requests.post(
        system_endpoint.format(path=f"play/{game_name_url}"), json={
            "user_id": player_id,
            "game_id": game_id,
            **specific_game_player_action_params,
            "user_signature": b64encode(player_signing_key.sign(format_message({
                "user_id": player_id,
                "action_number": player_action_number + 1,
                "game_name": game_name,
                "game_id": game_id,
                "game_revision": game_revision,
                "game_action_number": 1,
                **specific_game_player_action_params,
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 409
    assert payload ==  {"detail": ["Game is not active"]}


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params, specific_game_player_action_params", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5}, {"action": "next"})
])
def test_play_with_insufficient_balance(
    system_endpoint,
    host_endpoint,
    host_user_signing_key,
    game_name,
    game_name_url,
    specific_game_params,
    specific_game_player_action_params
):
    # create player
    new_player_signing_key = SigningKey.generate()
    new_player_public_key = new_player_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(new_player_public_key).decode()
        }
    )
    payload = response.json()
    new_player_id = payload["id"]
    new_player_action_number = 0
    # get host_user data
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
    # create game
    requests.post(system_endpoint.format(path=f"faucet/{host_user_id}"), json={})
    requests.post(host_endpoint.format(path="faucet"), json={})
    response = requests.post(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": host_user_id,
            "bet": 50,
            "duration": 60,
            "active": True,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": None,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 1,
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
    game_id = payload["id"]
    game_revision = payload["action_number"]
    # try to start game
    response = requests.post(
        system_endpoint.format(path=f"play/{game_name_url}"), json={
            "user_id": new_player_id,
            "game_id": game_id,
            **specific_game_player_action_params,
            "user_signature": b64encode(new_player_signing_key.sign(format_message({
                "user_id": new_player_id,
                "action_number": new_player_action_number + 1,
                "game_name": game_name,
                "game_id": game_id,
                "game_revision": game_revision,
                "game_action_number": 1,
                **specific_game_player_action_params,
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 409
    assert payload ==  {"detail": ["Insufficient balance"]}


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params, specific_game_player_action_params", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5}, {"action": "next"})
])
def test_host_user_try_to_play(
    system_endpoint,
    host_endpoint,
    host_user_signing_key,
    game_name,
    game_name_url,
    specific_game_params,
    specific_game_player_action_params
):
    # get host_user data
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
    # create game
    requests.post(system_endpoint.format(path=f"faucet/{host_user_id}"), json={})
    requests.post(host_endpoint.format(path="faucet"), json={})
    response = requests.post(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": host_user_id,
            "bet": 50,
            "duration": 60,
            "active": True,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": None,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 1,
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
    game_id = payload["id"]
    game_revision = payload["action_number"]
    # try to start game
    response = requests.post(
        system_endpoint.format(path=f"play/{game_name_url}"), json={
            "user_id": host_user_id,
            "game_id": game_id,
            **specific_game_player_action_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "user_id": host_user_id,
                "action_number": host_user_action_number + 2,
                "game_name": game_name,
                "game_id": game_id,
                "game_revision": game_revision,
                "game_action_number": 1,
                **specific_game_player_action_params,
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 409
    assert payload ==  {"detail": ["You can't play from an account where a host is set"]}


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params, specific_game_player_action_params, specific_game_action_attributes", [
    ("optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5}, {"action": "next"}, ["number"])
])
def test_play_timeout(
    system_endpoint,
    host_endpoint,
    host_user_signing_key,
    system_verifying_key,
    game_name,
    game_name_url,
    specific_game_params,
    specific_game_player_action_params,
    specific_game_action_attributes
):
    # create player
    new_player_signing_key = SigningKey.generate()
    new_player_public_key = new_player_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(new_player_public_key).decode()
        }
    )
    payload = response.json()
    new_player_id = payload["id"]
    new_player_action_number = 0
    # get host_user data
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
    host_user_balance = payload["balance"]
    # create game
    requests.post(system_endpoint.format(path=f"faucet/{host_user_id}"), json={})
    requests.post(host_endpoint.format(path="faucet"), json={})
    game_duration = 10
    response = requests.post(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": host_user_id,
            "bet": 50,
            "duration": game_duration,
            "active": True,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": None,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 1,
                "game_name": game_name,
                "bet": 50,
                "duration": game_duration,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    game_id = payload["id"]
    game_revision = payload["action_number"]
    # start game
    def get_player_balance():
        response = requests.get(system_endpoint.format(path=f"users/{new_player_id}"))
        return response.json()["balance"]

    def get_host_user_balance():
        system_response = requests.get(system_endpoint.format(path=f"users/{host_user_id}"))
        host_response = requests.get(host_endpoint.format(path="users"))
        return system_response.json()["balance"] - host_user_balance, host_response.json()["balance"] - host_user_balance

    requests.post(system_endpoint.format(path=f"faucet/{new_player_id}"), json={})
    response = requests.post(
        system_endpoint.format(path=f"play/{game_name_url}"), json={
            "user_id": new_player_id,
            "game_id": game_id,
            **specific_game_player_action_params,
            "user_signature": b64encode(new_player_signing_key.sign(format_message({
                "user_id": new_player_id,
                "action_number": new_player_action_number + 1,
                "game_name": game_name,
                "game_id": game_id,
                "game_revision": game_revision,
                "game_action_number": 1,
                **specific_game_player_action_params,
            }))).decode()
        }
    )
    payload = response.json()
    assert response.status_code == 200
    system_verifying_key.verify(
        b64decode(payload["system_signature"]),
        format_message({
            "action_number": new_player_action_number + 1,
            "game_name": game_name,
            "game_revision": game_revision,
            "game_action_number": 1,
            "created_at": payload["created_at"],
            **{attr: payload[attr] for attr in specific_game_action_attributes}
        })
    )
    assert get_player_balance() == 50
    assert get_host_user_balance() == (50, 50)
    time.sleep(game_duration + 1)
    assert get_player_balance() == 50
    assert get_host_user_balance() == (150, 150)


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params, specific_game_player_actions_params, specific_game_action_attributes", [
    (
            "optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5},
            [{"action": "next"}, {"action": "stop"}], ["number"]
    )
])
def test_play_player_wins(
    system_endpoint,
    host_endpoint,
    host_user_signing_key,
    system_verifying_key,
    game_name,
    game_name_url,
    specific_game_params,
    specific_game_player_actions_params,
    specific_game_action_attributes
):
    # create player
    player_signing_key = SigningKey.generate()
    player_public_key = player_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(player_public_key).decode()
        }
    )
    payload = response.json()
    player_id = payload["id"]
    player_action_number = 0
    # get host_user data
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
    host_user_balance = payload["balance"]
    # create game
    requests.post(system_endpoint.format(path=f"faucet/{host_user_id}"), json={})
    requests.post(host_endpoint.format(path="faucet"), json={})
    game_duration = 10
    response = requests.post(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": host_user_id,
            "bet": 50,
            "duration": game_duration,
            "active": True,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": None,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 1,
                "game_name": game_name,
                "bet": 50,
                "duration": game_duration,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    game_id = payload["id"]
    game_revision = payload["action_number"]
    # start game
    def get_player_balance():
        response = requests.get(system_endpoint.format(path=f"users/{player_id}"))
        return response.json()["balance"]

    def get_host_user_balance():
        system_response = requests.get(system_endpoint.format(path=f"users/{host_user_id}"))
        host_response = requests.get(host_endpoint.format(path="users"))
        return system_response.json()["balance"] - host_user_balance, host_response.json()["balance"] - host_user_balance

    requests.post(system_endpoint.format(path=f"faucet/{player_id}"), json={})

    for i, specific_game_player_action_param in enumerate(specific_game_player_actions_params):
        response = requests.post(
            system_endpoint.format(path=f"play/{game_name_url}"), json={
                "user_id": player_id,
                "game_id": game_id,
                **specific_game_player_action_param,
                "user_signature": b64encode(player_signing_key.sign(format_message({
                    "user_id": player_id,
                    "action_number": player_action_number + 1 + i,
                    "game_name": game_name,
                    "game_id": game_id,
                    "game_revision": game_revision,
                    "game_action_number": 1 + i,
                    **specific_game_player_action_param,
                }))).decode()
            }
        )
        payload = response.json()
        assert response.status_code == 200
        if i != len(specific_game_player_actions_params) - 1:
            system_verifying_key.verify(
                b64decode(payload["system_signature"]),
                format_message({
                    "action_number": player_action_number + 1 + i,
                    "game_name": game_name,
                    "game_revision": game_revision,
                    "game_action_number": 1 + i,
                    "created_at": payload["created_at"],
                    **{attr: payload[attr] for attr in specific_game_action_attributes}
                })
            )
    # a delay to ensure the celery were tasks executed
    time.sleep(1)

    assert get_player_balance() == 150
    assert get_host_user_balance() == (50, 50)


@pytest.mark.parametrize("game_name, game_name_url, specific_game_params, specific_game_player_actions_params, specific_game_action_attributes", [
    (
        "optimal stopping", "optimal_stopping", {"numbers_count": 15, "mean": 500, "std": 500, "top": 5},
        [{"action": "next"}, {"action": "next"}, {"action": "stop"}], ["number"]
    )
])
def test_play_host_user_wins(
    system_endpoint,
    host_endpoint,
    host_user_signing_key,
    system_verifying_key,
    game_name,
    game_name_url,
    specific_game_params,
    specific_game_player_actions_params,
    specific_game_action_attributes
):
    # create player
    player_signing_key = SigningKey.generate()
    player_public_key = player_signing_key.get_verifying_key().to_der()
    response = requests.post(
        system_endpoint.format(path="users"), json={
            "public_key": b64encode(player_public_key).decode()
        }
    )
    payload = response.json()
    player_id = payload["id"]
    player_action_number = 0
    # get host_user data
    response = requests.get(host_endpoint.format(path="users"))
    payload = response.json()
    host_user_id = payload["id"]
    host_user_action_number = payload["action_number"]
    host_user_balance = payload["balance"]
    # create game
    requests.post(system_endpoint.format(path=f"faucet/{host_user_id}"), json={})
    requests.post(host_endpoint.format(path="faucet"), json={})
    game_duration = 10
    response = requests.post(
        host_endpoint.format(path=f"games/{game_name_url}"), json={
            "user_id": host_user_id,
            "bet": 50,
            "duration": game_duration,
            "active": True,
            "seed": b64encode(b"12345678").decode(),
            **specific_game_params,
            "user_signature": b64encode(host_user_signing_key.sign(format_message({
                "id": None,
                "user_id": host_user_id,
                "action_number": host_user_action_number + 1,
                "game_name": game_name,
                "bet": 50,
                "duration": game_duration,
                "active": True,
                "seed_hash": b64encode(sha256(b"12345678").digest()).decode(),
                "seed": None,
                **specific_game_params
            }))).decode()
        }
    )
    payload = response.json()
    game_id = payload["id"]
    game_revision = payload["action_number"]
    # start game
    def get_player_balance():
        response = requests.get(system_endpoint.format(path=f"users/{player_id}"))
        return response.json()["balance"]

    def get_host_user_balance():
        system_response = requests.get(system_endpoint.format(path=f"users/{host_user_id}"))
        host_response = requests.get(host_endpoint.format(path="users"))
        return system_response.json()["balance"] - host_user_balance, host_response.json()["balance"] - host_user_balance

    requests.post(system_endpoint.format(path=f"faucet/{player_id}"), json={})

    for i, specific_game_player_action_param in enumerate(specific_game_player_actions_params):
        response = requests.post(
            system_endpoint.format(path=f"play/{game_name_url}"), json={
                "user_id": player_id,
                "game_id": game_id,
                **specific_game_player_action_param,
                "user_signature": b64encode(player_signing_key.sign(format_message({
                    "user_id": player_id,
                    "action_number": player_action_number + 1 + i,
                    "game_name": game_name,
                    "game_id": game_id,
                    "game_revision": game_revision,
                    "game_action_number": 1 + i,
                    **specific_game_player_action_param,
                }))).decode()
            }
        )
        payload = response.json()
        assert response.status_code == 200
        if i != len(specific_game_player_actions_params) - 1:
            system_verifying_key.verify(
                b64decode(payload["system_signature"]),
                format_message({
                    "action_number": player_action_number + 1 + i,
                    "game_name": game_name,
                    "game_revision": game_revision,
                    "game_action_number": 1 + i,
                    "created_at": payload["created_at"],
                    **{attr: payload[attr] for attr in specific_game_action_attributes}
                })
            )
    # a delay to ensure the celery were tasks executed
    time.sleep(1)

    assert get_player_balance() == 50
    assert get_host_user_balance() == (150, 150)
