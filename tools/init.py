from hashlib import sha256

from ecdsa import SigningKey, SECP256k1


system_signing_key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
system_verifying_key = system_signing_key.get_verifying_key()

host_user_signing_key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
host_user_verifying_key = host_user_signing_key.get_verifying_key()

player_signing_key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
player_verifying_key = player_signing_key.get_verifying_key()


with open("../system/keys/system_private_key.der", "wb") as f:
    f.write(system_signing_key.to_der())
with open("../system/keys/system_public_key.der", "wb") as f:
    f.write(system_verifying_key.to_der())

with open("../host/keys/host_user_private_key.der", "wb") as f:
    f.write(host_user_signing_key.to_der())
with open("../host/keys/host_user_public_key.der", "wb") as f:
    f.write(host_user_verifying_key.to_der())
with open("../host/keys/system_public_key.der", "wb") as f:
    f.write(system_verifying_key.to_der())

with open("../player/keys/player_private_key.der", "wb") as f:
    f.write(player_signing_key.to_der())
with open("../player/keys/player_public_key.der", "wb") as f:
    f.write(player_verifying_key.to_der())
