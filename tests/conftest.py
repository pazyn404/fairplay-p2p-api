import pytest
from ecdsa import SigningKey, VerifyingKey


@pytest.fixture(scope="session")
def system_verifying_key():
    with open("system/keys/system_public_key.der", "rb") as f:
        system_public_key = f.read()

    return VerifyingKey.from_der(system_public_key)


@pytest.fixture(scope="session")
def host_user_signing_key():
    with open("host/keys/host_user_private_key.der", "rb") as f:
        host_private_key = f.read()

    return SigningKey.from_der(host_private_key)


@pytest.fixture(scope="session")
def system_endpoint():
    return "http://127.0.0.1:8000/{path}"


@pytest.fixture(scope="session")
def host_endpoint():
    return "http://127.0.0.1:5000/{path}"
