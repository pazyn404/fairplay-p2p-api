from config import logger
from exceptions import VerificationError


def format_system_verification_errors(
        errors: list[VerificationError],
        *,
        system_payload: dict[str, int | str] | None = None,
        user_payload: dict[str, int | str] | None = None
) -> tuple[dict[str, list[str]], int]:
    logger.critical(errors, extra={"system_payload": system_payload, "user_payload": user_payload})

    errors.sort(key=lambda x: x.status_code, reverse=True)
    return {"system_errors": [str(error) for error in errors]}, errors[-1].status_code
