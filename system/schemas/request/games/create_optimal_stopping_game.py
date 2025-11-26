from typing import Annotated

from pydantic import Field

from .base_create_game import BaseCreateGameRequestSchema


class CreateOptimalStoppingGameRequestSchema(BaseCreateGameRequestSchema):
    numbers_count: Annotated[int, Field(gt=9, lt=51)]
    std: Annotated[int, Field(gt=99, lt=1001)]
    mean: Annotated[int, Field(gt=-1, lt=1001)]
    top: Annotated[int, Field(gt=0, lt=51)]
