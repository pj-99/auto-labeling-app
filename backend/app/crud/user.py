from uuid import uuid4

from models.user import User
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_user_if_not_exists(
    db: AsyncIOMotorDatabase, clerk_user_id: str
) -> tuple[bool, User]:
    """Create a user if not exists.

    Returns:
        tuple[bool, User]: (True, user) if created, (False, user) if exists
    """
    user = await db["users"].find_one({"clerk_user_id": clerk_user_id})
    if user:
        return False, User(**user)
    else:
        new_user = User(id=uuid4(), clerk_user_id=clerk_user_id)
        await db["users"].insert_one(new_user.model_dump())
        return True, new_user
