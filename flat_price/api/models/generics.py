from typing import Any
from typing import Optional

from pydantic import BaseModel
from pydantic import fields


class BaseData(BaseModel):
    stats: "Stats"


class BaseResponse(BaseModel):
    success: bool
    data: Any


class Pagination(BaseModel):
    page: int
    pages: int


class Stats(BaseModel):
    count: int
    count_blocks: int = fields.Field(alias="countBlocks")
    page: Optional[int] = fields.Field(alias="currentPage", default=None)
    pages: Optional[int] = fields.Field(alias="lastPage", default=None)


BaseData.model_rebuild()
