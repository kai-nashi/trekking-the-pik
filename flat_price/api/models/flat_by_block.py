from pydantic import BaseModel
from pydantic import fields

from flat_price.api.models.generics import BaseData
from flat_price.api.models.generics import BaseResponse


class FlatsByBlock(BaseResponse):
    data: "Data"


class Data(BaseData):
    items: list["Flat"]


class Flat(BaseModel):
    id: int
    area: float
    block_name: str = fields.Field(alias="blockName")
    block_slug: str = fields.Field(alias="blockSlug")
    bulk_name: str = fields.Field(alias="bulkName")
    floor: int
    floor_max: int = fields.Field(alias="maxFloor")
    plan_ulr: str = fields.Field(alias="planUrl")
    price: float
    rooms: int
    status: str
    type_id: int = fields.Field(alias='typeId')


FlatsByBlock.model_rebuild()
