from exceptions import ViolatedConstraintError


def format_violated_constraint_errors(errors: list[ViolatedConstraintError]) -> tuple[dict[str, list[str]], int]:
    return {"errors": [str(error) for error in errors]}, 409
