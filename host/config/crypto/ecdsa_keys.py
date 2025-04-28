from ecdsa import SigningKey, VerifyingKey
from ecdsa.der import UnexpectedDER
from ecdsa.keys import BadSignatureError

from .base_keys import BaseSigningKey, BaseVerifyingKey
from ..exceptions import InvalidSigningKey, InvalidVerifyingKey, InvalidSignature


class EcdsaSigningKey(BaseSigningKey):
    def __init__(self, private_key: bytes) -> None:
        try:
            self._signing_key = SigningKey.from_der(private_key)
        except UnexpectedDER:
            raise InvalidSigningKey

    @property
    def key(self) -> bytes:
        return self._signing_key.to_der()

    def sign(self, message: bytes) -> bytes:
        return self._signing_key.sign(message)


class EcdsaVerifyingKey(BaseVerifyingKey):
    def __init__(self, public_key: bytes) -> None:
        try:
            self._verifying_key = VerifyingKey.from_der(public_key)
        except UnexpectedDER:
            raise InvalidVerifyingKey

    @property
    def key(self) -> bytes:
        return self._verifying_key.to_der()

    def verify(self, message: bytes, signature: bytes) -> None:
        try:
            self._verifying_key.verify(signature, message)
        except BadSignatureError:
            raise InvalidSignature
