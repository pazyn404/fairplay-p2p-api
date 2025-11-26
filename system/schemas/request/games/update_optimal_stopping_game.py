from typing import Annotated

from pydantic import Field

from .base_update_game import BaseUpdateGameRequestSchema


class UpdateOptimalStoppingGameRequestSchema(BaseUpdateGameRequestSchema):
    numbers_count: Annotated[int, Field(gt=9, lt=51)] | None = None
    std: Annotated[int, Field(gt=99, lt=1001)] | None = None
    mean: Annotated[int, Field(gt=-1, lt=1001)] | None = None
    top: Annotated[int, Field(gt=0, lt=51)] | None = None
