import abc
import datetime
import json
import os

from botocore.client import BaseClient
from botocore.response import StreamingBody
from github.ContentFile import ContentFile
from github.Repository import Repository
from pydantic import BaseModel
from pydantic import field_validator
from pydantic import fields


__all__ = [
    'FlatsSource',
    'FlatsSourceLocalFile',
    'FlatsSourceS3',
    'FileS3',
]

from trekking_the_pik.models.blocks import Flat


class FlatsSource(abc.ABC):
    def __init__(self):
        self.data = []
        self._file = None
        self._raw_data: str = ''

    def __getitem__(self, index) -> Flat:
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def add(self, flat: Flat):
        self.data.append(flat)

    @property
    def file(self):
        if self._file:
            return self._file

        self.retrieve()
        return self._file

    @file.setter
    def file(self, value):
        self._file = value

    def get(self, flat_id: int) -> Flat | None:
        return next((flat for flat in self if flat.id == flat_id), None)

    def load(self) -> list[Flat]:
        """Call"""
        self._file = self.retrieve()
        self.data = [Flat(**flat) for flat in json.loads(self.raw_data)]
        return self.data

    @property
    @abc.abstractmethod
    def raw_data(self) -> str:
        """Cached json data from source"""
        raise NotImplemented()

    @abc.abstractmethod
    def retrieve(self):
        """Load json data from source"""
        raise NotImplemented()

    def to_json(self):
        data = [json.loads(flat.model_dump_json()) for flat in self]
        return json.dumps(data, indent=4, ensure_ascii=False)

    def update(self) -> bool:
        """Update source data if it has been changed"""
        json_data = self.to_json()
        update_required = json_data != self.raw_data

        if update_required:
            self.upload(json_data)

        return update_required

    @abc.abstractmethod
    def upload(self, raw_data: str):
        """Update json in source"""
        raise NotImplemented()


class FlatsSourceGit(FlatsSource):
    file: ContentFile

    def __init__(self, repo: Repository, file_path: str):
        super(FlatsSourceGit, self).__init__()
        self.file_path = file_path
        self.repo = repo

    def retrieve(self) -> ContentFile:
        return self.repo.get_contents(self.file_path)

    @property
    def raw_data(self) -> str:
        return self.file.decoded_content.decode('utf-8')

    def upload(self, raw_data: str):
        path = self.file_path
        if path.startswith('/'):
            path = path[1:]

        self.repo.update_file(path, "chore: flats.json /auto", raw_data, self.file.sha)


class FlatsSourceLocalFile(FlatsSource):
    file: str

    def __init__(self, file_path: str):
        super(FlatsSourceLocalFile, self).__init__()
        self.file_path = file_path

    def retrieve(self) -> str:
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"`{self.file_path}` is not exists")

        with open(self.file_path, 'r', encoding="utf-8") as file:
            return file.read()

    @property
    def raw_data(self) -> str:
        return self.file

    def upload(self, raw_data: str):
        with open(self.file_path, 'w', encoding="utf-8") as file:
            file.write(raw_data)


class FlatsSourceS3(FlatsSource):
    file: "FileS3"

    def __init__(self, client: BaseClient, bucket: str, key: str, storage_class: str | None):
        super(FlatsSourceS3, self).__init__()
        self.client = client
        self.bucket = bucket
        self.key = key
        self.storage_class = storage_class

    def check_bucket_exists(self):
        self.client.head_bucket(Bucket=self.bucket)

    def retrieve(self) -> "FileS3":
        self.check_bucket_exists()
        file = self.client.get_object(Bucket=self.bucket, Key=self.key)
        return FileS3(**file)

    @property
    def raw_data(self) -> str:
        return self.file.raw_data

    def upload(self, raw_data: str):
        self.check_bucket_exists()
        self.client.put_object(Bucket=self.bucket, Key=self.key, Body=raw_data, StorageClass=self.storage_class)


class FileS3(BaseModel):
    body: StreamingBody = fields.Field(alias='Body')
    last_modified: datetime.datetime = fields.Field(alias='LastModified')
    raw_data: str = fields.Field('', validate_default=True)
    response_metadata: dict = fields.Field(alias='ResponseMetadata')

    class Config:
        arbitrary_types_allowed = True

    @field_validator('raw_data')
    def raw_data_setter(cls, value, values):
        body = values.data.get('body')
        return body.read().decode('utf-8') if body else ''
