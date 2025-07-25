from .verification_error import VerificationError


class InvalidVerifyingKey(VerificationError):
    def __init__(self, message: str = "Invalid public key") -> None:
        super().__init__(message, 400)
