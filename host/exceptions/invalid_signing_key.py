from .verification_error import VerificationError


class InvalidSigningKey(VerificationError):
    def __init__(self, message: str = "Invalid private key") -> None:
        super().__init__(message, 400)
