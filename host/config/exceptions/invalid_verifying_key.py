from .verification_error import VerificationError


class InvalidVerifyingKey(VerificationError):
    def __init__(self, message="Invalid public key"):
        super().__init__(message, 400)
