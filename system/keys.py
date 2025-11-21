from os import environ

from crypto import EcdsaSigningKey, EcdsaVerifyingKey


SigningKey = EcdsaSigningKey
VerifyingKey = EcdsaVerifyingKey

with open(environ["SYSTEM_PRIVATE_KEY_PATH"], "rb") as f:
    system_private_key = f.read()

with open(environ["SYSTEM_PUBLIC_KEY_PATH"], "rb") as f:
    system_public_key = f.read()

SYSTEM_SIGNING_KEY = SigningKey(system_private_key)
SYSTEM_VERIFYING_KEY = VerifyingKey(system_public_key)
