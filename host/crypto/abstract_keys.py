from abc import ABC, abstractmethod


class AbstractKey(ABC):
    @property
    @abstractmethod
    def key(self):
        pass


class AbstractSigningKey(AbstractKey):
    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        pass


class AbstractVerifyingKey(AbstractKey):
    @abstractmethod
    def verify(self, message: bytes, signature: bytes) -> None:
        pass
