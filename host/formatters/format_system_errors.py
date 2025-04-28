from config import logger


def format_system_errors(errors, status_code, *, system_payload=None, user_payload=None):
    logger.critical(errors, extra={"system_payload": system_payload, "user_payload": user_payload})

    return {"system_errors": errors}, status_code
