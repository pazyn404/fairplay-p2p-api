from .verification_error import VerificationError


class InvalidSignature(VerificationError):
    def __init__(self, message: str = "Invalid signature") -> None:
        super().__init__(message, 401)
