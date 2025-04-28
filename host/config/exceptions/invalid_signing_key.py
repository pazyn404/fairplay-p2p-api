from .verification_error import VerificationError


class InvalidSigningKey(VerificationError):
    def __init__(self, message="Invalid private key"):
        super().__init__(message, 400)
