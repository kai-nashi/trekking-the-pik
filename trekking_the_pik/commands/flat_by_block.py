import json
import logging
import os.path
from collections import UserDict
from typing import Iterable
from typing import Self

import click

from trekking_the_pik.api import Block
from trekking_the_pik.api import client as pik
from trekking_the_pik.conf import settings
from trekking_the_pik.models.blocks import Change
from trekking_the_pik.models.blocks import Flat


stream_handler = logging.StreamHandler()

logger = logging.Logger(__name__)
logger.setLevel("DEBUG")
logger.addHandler(stream_handler)


class FlatsList(UserDict):
    def __init__(self, flats: list[Flat]):
        super(FlatsList, self).__init__()
        for flat in flats:
            self[flat.id] = flat

    @classmethod
    def from_file(cls, path: str) -> Self:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"`{path}` is not exists")

        with open(settings.flats_file_path, 'r', encoding="utf-8") as file:
            data = file.read()
            return cls.from_json(data)

    @classmethod
    def from_json(cls, data: str) -> Self:
        data_json = json.loads(data)
        flats = [Flat.model_validate(flat_json) for flat_json in data_json]
        return cls(flats=flats)

    def save_to_file(self, path: str):
        result = [json.loads(flat.model_dump_json()) for flat in self.values()]
        with open(path, 'w', encoding="utf-8") as file:
            file.write(json.dumps(result, indent=4, ensure_ascii=False))


def get_blocks_filtered(blocks_only: list[int | str] = None) -> list[Block]:
    blocks = pik.get_blocks()

    if blocks_only:
        blocks_only = [int(_v) if _v.isdigit() else _v for _v in blocks_only]
        blocks = [block for block in blocks if {block.id, block.name} & set(blocks_only)]

    return blocks


@click.command
@click.option('--block', '-b', 'blocks_only', multiple=True, type=str)
def update(blocks_only: list[str]):
    flats = FlatsList.from_file(settings.flats_file_path)
    flats_processed = set()

    blocks = get_blocks_filtered(blocks_only=blocks_only)
    for block in blocks:
        flats_api = pik.get_all_pages(
            pik.get_flats_by_block,
            block_id=block.id,
            current_benefit='polnaya-oplata',
            only_flats=True,
            order_by='asc',
            sort_by='price',
        )

        for flat_api in flats_api:
            created = False
            if not (flat := flats.get(flat_api.id)):
                flat = Flat(id=flat_api.id, block_id=block.id)
                flats[flat.id] = flat
                created = True

            flat.update(flat_api, track_changes=not created)
            flats_processed.add(flat_api.id)

    flats_sold = set(flats) - flats_processed
    for flat_id in flats_sold:
        flat = flats[flat_id]
        if flat.status == 'sold':
            continue

        flat.changelog.append(Change(key='status', value=flat.status, value_new='sold'))
        flat.status = 'sold'

    flats.save_to_file(settings.flats_file_path)


if __name__ == '__main__':
    params = {
        '--block': [1724, 2014]
    }

    args = []
    for key, value in params.items():
        if isinstance(value, Iterable):
            [args.extend([key, _v]) for _v in value]
        else:
            args.extend([key, value])

    update(args)
