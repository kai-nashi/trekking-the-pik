import datetime
from typing import Any
from typing import Literal
from typing import Self

from pydantic import BaseModel
from pydantic import fields

from flat_price.api.models.flat_by_block import Flat as FlatApi


FLAT_STATUS = Literal['free', 'reserve', 'sold']


class PriceHistory(BaseModel):
    created_at: datetime.datetime = fields.Field(default_factory=datetime.datetime.now)
    price: float


class StatusHistory(BaseModel):
    created_at: datetime.datetime = fields.Field(default_factory=datetime.datetime.now)
    status: FLAT_STATUS


class Flat(BaseModel):
    id: int
    area: float = None
    changelog: list["Change"] = fields.Field(default_factory=list)
    block_id: int = None
    block_name: str = None
    block_slug: str = None
    bulk_name: str = None
    created_at: datetime.datetime = fields.Field(default_factory=datetime.datetime.now)
    floor: int = None
    price: float = fields.Field(None, alias='price')
    rooms: int = None
    status: FLAT_STATUS = fields.Field(None, alias='status')

    class Config:
        track_keys = ('id', 'area', 'block_name', 'block_slug', 'bulk_name', 'floor', 'price', 'rooms', 'status')

    def __eq__(self, other: Self | FlatApi) -> bool:
        for key in self.model_config['track_keys']:
            if getattr(self, key) != getattr(other, key):
                return False

        return True

    def update(self, flat_api: FlatApi, track_changes: bool = True):
        if self.id != flat_api.id:
            raise ValueError('Could not update flats with different `id`')

        if self == flat_api:
            return

        for key in self.model_config['track_keys']:
            value = getattr(self, key)
            value_new = getattr(flat_api, key)

            if value == value_new:
                continue

            setattr(self, key, value_new)
            if track_changes:
                self.changelog.append(Change(key=key, value=value, value_new=value_new))


class Change(BaseModel):
    created_at: datetime.datetime = fields.Field(default_factory=datetime.datetime.now)
    key: str
    value: Any
    value_new: Any


Flat.model_rebuild()
