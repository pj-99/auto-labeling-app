# Dependencies for the API
from typing import AsyncGenerator

from core.config import Settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

settings = Settings()


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
