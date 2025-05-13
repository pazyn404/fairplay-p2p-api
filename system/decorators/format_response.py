import functools

from starlette.responses import JSONResponse

from formatters import format_data


def format_response(f):
    @functools.wraps(f)
    async def inner(*args, **kwargs):
        data, status_code = await f(*args, **kwargs)
        formatted_data = format_data(data)

        return JSONResponse(formatted_data, status_code)

    return inner
