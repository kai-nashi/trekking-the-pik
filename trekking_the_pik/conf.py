import github
from github import Auth
from pydantic import fields
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    flats_file_path: str | None = fields.Field(None, alias="FLATS_FILE_PATH")
    flats_repo: str = fields.Field(alias="FLATS_REPO")
    flats_repo_file_path: str = fields.Field(alias="FLATS_REPO_FILE_PATH")
    flats_repo_token: str = fields.Field(alias="FLATS_REPO_TOKEN")


settings = Settings()

git_auth = auth = Auth.Token(settings.flats_repo_token)
git = github.Github(auth=git_auth)
repo_flats = git.get_user().get_repo(settings.flats_repo)
