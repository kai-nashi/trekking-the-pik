from trekking_the_pik import data
from trekking_the_pik.conf import settings
from trekking_the_pik.conf import yandex_s3
from trekking_the_pik.data import FlatsSourceS3


def flats_update_handler(event, context):
    source = FlatsSourceS3(yandex_s3, settings.yandex_aws_bucket, settings.yandex_aws_flats_key, storage_class='STANDARD')
    updater = data.Updater(source)
    updater.update([1724, 2014])

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'isBase64Encoded': False,
        'body': 'ok'
    }
