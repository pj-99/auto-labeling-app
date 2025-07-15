from typing import Union
from uuid import UUID

import bson
from models.image import Image
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_image(
    db: AsyncIOMotorDatabase, user_id: UUID, image_id: UUID
) -> Union[Image, None]:
    result = await db["images"].find_one({"id": image_id})
    if result is None:
        return None

    # For legacy issue, some created_by stores as a string
    if str(result["created_by"]) != str(user_id):
        print("user_id mismatch", result["created_by"], user_id)
        return None

    return Image(**result)
