from pydantic import BaseModel


class ErrorResponseSchema(BaseModel):
    detail: list[str]
