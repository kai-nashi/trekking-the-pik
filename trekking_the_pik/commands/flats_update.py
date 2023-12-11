import logging
from typing import Iterable

import click

from trekking_the_pik import data
from trekking_the_pik.conf import settings
from trekking_the_pik.conf import yandex_s3
from trekking_the_pik.data import FlatsSourceS3

stream_handler = logging.StreamHandler()

logger = logging.Logger('flats_update')
logger.setLevel("DEBUG")
logger.addHandler(stream_handler)


@click.command
@click.option('--block', '-b', 'blocks_only', multiple=True, type=str)
def command(blocks_only: list[str]):
    source = FlatsSourceS3(yandex_s3, settings.yandex_aws_bucket, settings.yandex_aws_flats_key, storage_class='STANDARD')
    updater = data.Updater(source)
    updater.update([int(block) for block in blocks_only])


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

    command(args)
