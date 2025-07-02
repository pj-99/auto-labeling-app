import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    print("ENV:", os.getenv("ENV"))
    # Default env file
    if os.getenv("ENV") == "prod":
        model_config = SettingsConfigDict(env_file="prod.env")
    else:
        model_config = SettingsConfigDict(env_file="dev.env")

    MONGO_URL: str
