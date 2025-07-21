from copy import copy
from base64 import b64encode
from typing import Any


def format_data(data: Any) -> Any:
    formatted_data = copy(data)
    if isinstance(formatted_data, dict):
        for param, val in formatted_data.items():
            formatted_data[param] = format_data(val)
    elif isinstance(formatted_data, list):
        for i, item in enumerate(formatted_data):
            formatted_data[i] = format_data(item)
    elif isinstance(formatted_data, bytes):
        formatted_data = b64encode(formatted_data).decode()

    return formatted_data
