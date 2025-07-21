def format_errors(errors: list[str], status_code: int) -> tuple[dict[str, list[str]], int]:
    return {"errors": errors}, status_code
