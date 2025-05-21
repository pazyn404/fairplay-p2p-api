from app import db
from config import VerificationError
from models import User


class VerifyTimestampMixin:
    def verify_timestamp(self):
        if hasattr(self, "updated_at"):
            if self.updated_at < self.user.last_timestamp:
                raise VerificationError("Invalid timestamp", 409)
        else:
            if self.created_at < self.user.last_timestamp:
                raise VerificationError("Invalid timestamp", 409)
