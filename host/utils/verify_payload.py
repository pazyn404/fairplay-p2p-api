import binascii
from base64 import b64decode


def verify_payload(payload, structure, strict=True):
    filled = 0
    errors = []
    for param, info in structure.items():
        _type = info["type"]
        optional = info.get("optional", False)
        nullable = info.get("nullable", False)

        if param not in payload:
            if not optional:
                errors.append(f"{param} required")
            continue

        filled += 1

        val = payload[param]
        if val is None:
            if not nullable:
                errors.append(f"{param} is not nullable")
            continue

        if not isinstance(val, _type):
            errors.append(f"{param} is not {_type.__name__}")
            continue

        if _type is str:
            encoding = info.get("encoding")
            if encoding == "base64":
                try:
                    b64decode(val)
                except binascii.Error:
                    errors.append(f"{param} is not base64")
        elif _type is int:
            if "lt" in info:
                upper_bound = info["lt"] - 1
            elif "lte" in info:
                upper_bound = info["lte"]
            else:
                upper_bound = float("inf")

            if "gt" in info:
                lower_bound = info["gt"] + 1
            elif "gte" in info:
                lower_bound = info["gte"]
            else:
                lower_bound = float("-inf")

            if not lower_bound <= val <= upper_bound:
                errors.append(f"{param} is out of range")

    if strict and filled < len(payload):
        errors.append("Malformed payload")

    return errors
