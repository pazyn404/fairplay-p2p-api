from abc import ABC, abstractmethod


class BaseKey(ABC):
    @property
    @abstractmethod
    def key(self):
        pass


class BaseSigningKey(BaseKey):
    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        pass


class BaseVerifyingKey(BaseKey):
    @abstractmethod
    def verify(self, message: bytes, signature: bytes) -> None:
        pass
