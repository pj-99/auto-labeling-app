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
    CLERK_SECRET_KEY: str
    CLERK_JWT_PUB_KEY: str
    CLERK_JWT_KEY: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_credentials()

    def setup_credentials(self):
        if self.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                self.GOOGLE_APPLICATION_CREDENTIALS
            )
        if self.CLERK_JWT_PUB_KEY:
            with open(self.CLERK_JWT_PUB_KEY, "r") as f:
                self.CLERK_JWT_KEY = f.read()
