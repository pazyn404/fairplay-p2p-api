from os import environ

from crypto import EcdsaSigningKey, EcdsaVerifyingKey


SigningKey = EcdsaSigningKey
VerifyingKey = EcdsaVerifyingKey

with open(environ["USER_PRIVATE_KEY_PATH"], "rb") as f:
    host_private_key = f.read()

with open(environ["USER_PUBLIC_KEY_PATH"], "rb") as f:
    host_public_key = f.read()

with open(environ["SYSTEM_PUBLIC_KEY_PATH"], "rb") as f:
    system_public_key = f.read()

USER_SIGNING_KEY = SigningKey(host_private_key)
USER_VERIFYING_KEY = VerifyingKey(host_public_key)
SYSTEM_VERIFYING_KEY = VerifyingKey(system_public_key)
