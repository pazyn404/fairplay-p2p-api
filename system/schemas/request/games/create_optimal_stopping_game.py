from typing import Annotated

from pydantic import Field

from .base_create_game import BaseCreateGameRequestSchema


class CreateOptimalStoppingGameRequestSchema(BaseCreateGameRequestSchema):
    numbers_count: Annotated[int, Field(gt=10, lt=50)]
    std: Annotated[int, Field(gt=100, lt=1000)]
    mean: Annotated[int, Field(gt=0, lt=1000)]
    top: Annotated[int, Field(gt=1, lt=50)]
