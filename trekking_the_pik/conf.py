import github
from pydantic import fields
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str = fields.Field(alias="GITHUB_TOKEN")

    flats_file_path: str | None = fields.Field(alias="FLATS_FILE_PATH")
    flats_repo: str = fields.Field(alias="FLATS_REPO")
    flats_repo_file_path: str = fields.Field(alias="FLATS_REPO_FILE_PATH")


settings = Settings()
# git = github.Github(settings.github_token)
# repo_flats = git.get_user().get_repo(settings.flats_repo)
