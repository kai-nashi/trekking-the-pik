from pydantic import BaseModel
from pydantic import fields

from trekking_the_pik.api.models.generics import BaseData
from trekking_the_pik.api.models.generics import BaseResponse


class Blocks(BaseResponse):
    data: "Data"


class Block(BaseModel):
    id: int
    images: "Image" = fields.Field(alias='image')
    image_map: str = fields.Field(alias='mapImage')
    is_premium: bool = fields.Field(alias='isPremium')
    latitude: float
    longitude: float
    name: str
    path: str


class Data(BaseData):
    items: list[Block]


class Image(BaseModel):
    desktop: str
    mobile: str


Blocks.model_rebuild()
