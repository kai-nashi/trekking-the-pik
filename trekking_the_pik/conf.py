import boto3
from botocore.client import BaseClient
from pydantic import fields
from pydantic_settings import BaseSettings

from trekking_the_pik.api import Client as PikClient


class Settings(BaseSettings):
    yandex_aws_access_key_id: str = fields.Field(alias="YANDEX_AWS_ACCESS_KEY_ID")
    yandex_aws_secret_access_key: str = fields.Field(alias="YANDEX_AWS_SECRET_ACCESS_KEY")
    yandex_aws_bucket: str = fields.Field(alias="YANDEX_AWS_BUCKET")
    yandex_aws_flats_key: str = fields.Field(alias="YANDEX_AWS_FLATS_KEY")


settings = Settings()

pik = PikClient()
yandex_s3_session = boto3.session.Session()
yandex_s3: BaseClient = yandex_s3_session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=settings.yandex_aws_access_key_id,
    aws_secret_access_key=settings.yandex_aws_secret_access_key,
)
