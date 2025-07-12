import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    if os.getenv("ENV") == "prod":
        model_config = SettingsConfigDict(env_file="prod.env")
    else:
        model_config = SettingsConfigDict(env_file="dev.env")

    MONGO_URL: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_STORAGE_BUCKET: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_credentials()

    def setup_credentials(self):
        if self.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                self.GOOGLE_APPLICATION_CREDENTIALS
            )
