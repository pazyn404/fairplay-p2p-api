from .violated_constraint_error import ViolatedConstraintError


class ViolatedConstraintErrorsList(Exception):
    def __init__(self, errors: list[ViolatedConstraintError]) -> None:
        self._errors = errors

    @property
    def errors(self) -> list[str]:
        return [str(error) for error in self._errors]
