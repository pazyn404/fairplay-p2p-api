from config import logger


def format_system_errors(
        errors: list[str],
        status_code: int,
        *,
        system_payload: dict[str, int | str] | None = None,
        user_payload: dict[str, int | str] | None = None
) -> tuple[dict[str, list[str]], int]:
    logger.critical(errors, extra={"system_payload": system_payload, "user_payload": user_payload})

    return {"system_errors": errors}, status_code
