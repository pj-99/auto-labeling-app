# Dependencies for the API
import os
from typing import AsyncGenerator

from core.config import Settings
from google.cloud import storage
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

settings = Settings()


# TODO: singleton
def get_storage_client() -> storage.Client:

    return storage.Client()


def get_storage_bucket() -> storage.Bucket:
    client = get_storage_client()
    return client.bucket(settings.GCP_STORAGE_BUCKET)


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client: AsyncIOMotorClient = None
    try:
        print("Mongo URL:", settings.MONGO_URL)
        client = AsyncIOMotorClient(
            settings.MONGO_URL,
            uuidRepresentation="standard",  # This ensures proper UUID handling
            authSource="admin",
        )
        db = client.get_database(
            "app",
        )
        await client.admin.command("ping")
        yield db
    finally:
        if client:
            client.close()
