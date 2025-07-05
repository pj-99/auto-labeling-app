from uuid import UUID

import bson
from models.image import Image
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_image(db: AsyncIOMotorDatabase, user_id: UUID, image_id: UUID) -> Image:
    result = await db["images"].find_one({"id": bson.Binary.from_uuid(image_id)})
    if result is None:
        raise ValueError("Image not found")
    return Image(**result)
