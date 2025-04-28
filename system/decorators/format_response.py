import functools

from formatters import format_data


def format_response(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        data, status_code = f(*args, **kwargs)
        formatted_data = format_data(data)

        return formatted_data, status_code

    return inner
