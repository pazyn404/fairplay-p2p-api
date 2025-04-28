from .verification_error import VerificationError


class InvalidSignature(VerificationError):
    def __init__(self, message="Invalid signature"):
        super().__init__(message, 401)
