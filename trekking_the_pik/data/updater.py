from trekking_the_pik.conf import pik
from trekking_the_pik.data import FlatsSource
from trekking_the_pik.data.logs import logger
from trekking_the_pik.models.blocks import Change
from trekking_the_pik.models.blocks import Flat


class Updater:
    def __init__(self, source: FlatsSource):
        self.source = source
        self.source.load()

    def update_block(self, block_id):
        logger.debug(f'Block<{block_id}>: get flats...\n{"-"*32}')
        flats_api = pik.get_all_pages(
            pik.get_flats_by_block,
            block_id=block_id,
            current_benefit='polnaya-oplata',
            only_flats=True,
            order_by='asc',
            sort_by='price',
        )
        logger.debug(f'{"-"*32}\nBlock<{block_id}>: {len(flats_api)} flat(s) to process. Updating...')

        flats_created = []
        flats_updated = []

        for flat_api in flats_api:
            _created = False
            if flat := self.source.get(flat_api.id):
                flats_updated.append(flat)
            else:
                flat = Flat(id=flat_api.id, block_id=block_id)
                self.source.add(flat)
                flats_created.append(flat)
                _created = True

            flat.update(flat_api, track_changes=not _created)

        flats_ids = [flat.id for flat in flats_api]
        flat_sold = [flat for flat in self.source if flat.block_id == block_id and flat.id not in flats_ids and flat.status != 'sold']

        for flat in flat_sold:
            if flat.status == 'sold':
                continue

            flat.changelog.append(Change(key='status', value=flat.status, value_new='sold'))
            flat.status = 'sold'

        logger.debug(f'Block<{block_id}>: {len(flats_created)} flat(s) has been created')
        logger.debug(f'Block<{block_id}>: {len(flats_updated)} flat(s) has been updated')
        logger.debug(f'Block<{block_id}>: {len(flat_sold)} flat(s) has been sold')
        logger.debug(f'Block<{block_id}>: {len(flats_api)} processed\n')

    def update(self, blocks: list[int]):
        logger.debug('Blocks: load...')
        blocks_to_update = [block for block in pik.get_blocks() if block.id in blocks]
        logger.debug(f'Blocks: {len(blocks_to_update)} block(s) to update\n')

        [self.update_block(block.id) for block in blocks_to_update]

        logger.debug(f'Update source json file...')
        updated = self.source.update()
        logger.debug('Updated!' if updated else 'Updating not required')

