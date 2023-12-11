from typing import Iterable

from trekking_the_pik.commands.flats_update import flats_update


def flats_update_handler(event, context):
    params = {
        '--block': [1724, 2014]
    }

    args = []
    for key, value in params.items():
        if isinstance(value, Iterable):
            [args.extend([key, _v]) for _v in value]
        else:
            args.extend([key, value])

    flats_update(args)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'isBase64Encoded': False,
        'body': 'ok'
    }
