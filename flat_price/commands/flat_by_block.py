import json
import logging
from typing import Iterable

import click

from flat_price.api import client as pik
from flat_price.models.blocks import Change
from flat_price.models.blocks import Flat


stream_handler = logging.StreamHandler()

logger = logging.Logger(__name__)
logger.setLevel("DEBUG")
logger.addHandler(stream_handler)


@click.command
@click.option('--block', '-b', 'blocks_filter', multiple=True, type=str)
def update(blocks_filter: list[str]):
    with open('flats.json', 'r', encoding="utf-8") as file:
        data_str = file.read()
        data_json = json.loads(data_str)
        flats = {flat.id: flat for flat_json in data_json if (flat := Flat.model_validate(flat_json))}

    flats_processed = set()

    blocks = pik.get_blocks()

    if blocks_filter:
        blocks_filter = [int(_v) if _v.isdigit() else _v for _v in blocks_filter]
        blocks = [block for block in blocks if {block.id, block.name} & set(blocks_filter)]

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

    result = [json.loads(flat.model_dump_json()) for flat in flats.values()]
    with open('flats.json', 'w', encoding="utf-8") as file:
        file.write(json.dumps(result, indent=4, ensure_ascii=False))


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
