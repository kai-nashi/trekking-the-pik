import logging
import typing
from typing import TypeVar

import httpx
from httpx import Request
from httpx import Response
from httpx import USE_CLIENT_DEFAULT
from httpx._client import UseClientDefault
from httpx._types import AuthTypes
from pydantic import conint

from trekking_the_pik.api.models.blocks import Block
from trekking_the_pik.api.models.blocks import Blocks
from trekking_the_pik.api.models.flat_by_block import Flat
from trekking_the_pik.api.models.flat_by_block import FlatsByBlock
from trekking_the_pik.api.models.generics import Pagination

stream_handler = logging.StreamHandler()

logger = logging.Logger('pik')
logger.setLevel("DEBUG")
logger.addHandler(stream_handler)


MODEL = TypeVar('MODEL', bound=object)


class Client(httpx.Client):
    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html',
            'Content-Type': 'text/plain',
        }

        super().__init__(base_url='https://flat.pik-service.ru', headers=headers)

    def send(
        self,
        request: Request,
        *,
        stream: bool = False,
        auth: typing.Union[AuthTypes, UseClientDefault, None] = USE_CLIENT_DEFAULT,
        follow_redirects: typing.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
    ) -> Response:
        stream_handler.terminator = ' '

        logger.debug(f'{request.method} {request.url}')
        response = super(Client, self).send(request, stream=stream, auth=auth, follow_redirects=follow_redirects)

        stream_handler.terminator = '\n'
        logger.debug(response.status_code)

        return response

    @staticmethod
    def get_all_pages(
        method: callable,
        *args,
        **kwargs
    ) -> list:
        result = []
        page = 1
        pages = 1

        while page <= pages:
            result_api, pagination = method(*args, page=page, **kwargs)
            result.extend(result_api)

            page += 1
            pages = pagination.pages

        return result

    def get_blocks(self) -> list[Block]:
        response = self.get(url='/api/v1/filter/block')
        response.raise_for_status()
        blocks_response = Blocks.model_validate(response.json())
        return blocks_response.data.items

    def get_flats_by_block(
        self,
        block_id,
        *,
        current_benefit: str | None = None,
        page: conint(ge=1) = None,
        only_flats: bool = None,
        sort_by: str = None,
        order_by: typing.Literal['asc', 'desc'] = None
    ) -> (FlatsByBlock, Pagination):
        path = '/api/v1/filter/flat-by-block/{block_id}'.format(block_id=block_id)

        params = {
            'currentBenefit': current_benefit,
            'flatPage': page,
            'onlyFlats': int(only_flats),
            'sortBy': sort_by,
            'orderBy': order_by
        }

        response = self.get(path, params=params)
        response.raise_for_status()
        response_model = FlatsByBlock.model_validate(response.json())

        pagination = Pagination(
            page=response_model.data.stats.page,
            pages=response_model.data.stats.pages
        )

        return response_model.data.items, pagination


client = Client()
