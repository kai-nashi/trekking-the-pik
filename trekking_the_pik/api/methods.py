import httpx

from trekking_the_pik.api import logger
from trekking_the_pik.api.models.flat_by_block import Flat
from trekking_the_pik.api.models.flat_by_block import FlatsByBlock


def get_flats_by_block(complex_id, bulk_id) -> list[Flat]:
    url_base = '/api/v1/filter/flat-by-block/{id}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Accept': 'text/html',
        'Content-Type': 'text/plain',
    }

    params = {
        'currentBenefit': 'polnaya-oplata',
        'onlyFlats': 1,
        'bulk': bulk_id,
        'type': '1,2',
        'location': '81,86'
    }

    flats = []
    page = 1
    pages = 3

    while page <= pages:
        logger.debug(f'Retrieve {complex_id=} with {bulk_id=} {page=}')

        response = httpx.get(
            url_base.format(id=complex_id),
            params={'flatPage': page, **params},
            headers=headers
        )

        response.raise_for_status()

        response_model = FlatsByBlock.model_validate(response.json())
        flats.extend(response_model.data.items)

        pages = response_model.data.stats.pages
        page += 1

    return flats
