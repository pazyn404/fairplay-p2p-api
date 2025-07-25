from exceptions import VerificationError


def format_verification_errors(errors: list[VerificationError]) -> tuple[dict[str, list[str]], int]:
    errors.sort(key=lambda x: x.status_code, reverse=True)
    return {"errors": [str(error) for error in errors]}, errors[-1].status_code
