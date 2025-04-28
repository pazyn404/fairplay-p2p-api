from base64 import b64decode

from utils.verify_payload import verify_payload


def format_payload(payload, structure, strict=True):
    errors = verify_payload(payload, structure, strict)
    if errors:
        return {}, errors

    formatted_payload = {}
    for param, info in structure.items():
        if param not in payload:
            continue

        val = payload[param]
        formatted_payload[param] = val

        _type = info["type"]
        if _type is str:
            encoding = info.get("encoding")
            if val is not None and encoding == "base64":
                formatted_payload[param] = b64decode(val)

    return formatted_payload, errors
