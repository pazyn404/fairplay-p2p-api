from typing import Annotated

from pydantic import Field

from .base_update_game import BaseUpdateGameRequestSchema


class UpdateOptimalStoppingGameRequestSchema(BaseUpdateGameRequestSchema):
    numbers_count: Annotated[int, Field(gt=10, lt=50)] | None = None
    std: Annotated[int, Field(gt=100, lt=1000)] | None = None
    mean: Annotated[int, Field(gt=0, lt=1000)] | None = None
    top: Annotated[int, Field(gt=1, lt=50)] | None = None
