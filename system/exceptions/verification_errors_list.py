from .verification_error import VerificationError


class VerificationErrorsList(Exception):
    def __init__(self, errors: list[VerificationError]) -> None:
        self._errors = errors

        self._errors.sort(key=lambda x: x.status_code, reverse=True)

    @property
    def errors(self) -> list[str]:
        return [str(error) for error in self._errors]

    @property
    def status_code(self) -> int:
        return self._errors[-1].status_code
