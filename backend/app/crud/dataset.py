from datetime import datetime
from uuid import UUID, uuid4

import bson
from models.dataset import Dataset
from models.image import Image
from motor.motor_asyncio import AsyncIOMotorDatabase


def validate_user(user_id: UUID) -> bool:
    # TODO: validate user exist
    # TODO: maybe use middleware to validate user JWT
    return True


async def check_dataset_exists(db: AsyncIOMotorDatabase, dataset_id: UUID) -> bool:
    return await db["datasets"].find_one({"id": dataset_id}) is not None


async def insert_image_to_dataset(
    db: AsyncIOMotorDatabase,
    user_id: UUID,
    dataset_id: UUID,
    image_url: str,
    image_name: str,
) -> Image:
    if not await check_dataset_exists(db, dataset_id):
        raise ValueError("Dataset not found")

    if not validate_user(user_id):
        raise ValueError("User not found")

    try:
        # Insert to images collection
        image_id = uuid4()
        image = Image(
            id=image_id,
            image_name=image_name,
            image_url=image_url,
            created_by=user_id,
        )
        await db["images"].insert_one(image.model_dump(mode="json"))

        # Update the dataset collection
        await db["datasets"].update_one(
            {"id": dataset_id},
            {"$push": {"images": image_id}},
        )
        return image
    except Exception as e:
        raise e


async def create_dataset(db: AsyncIOMotorDatabase, user_id: UUID, name: str) -> Dataset:
    if not validate_user(user_id):
        raise ValueError("User not found")

    collection = db["datasets"]
    new_dataset_id = uuid4()
    user_id_binary = bson.Binary.from_uuid(user_id)
    dataset_id_binary = bson.Binary.from_uuid(new_dataset_id)

    doc = {
        "id": dataset_id_binary,
        "user_id": user_id_binary,
        "name": name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "images": [],
    }
    await collection.insert_one(doc)
    return Dataset(
        id=new_dataset_id,
        name=doc["name"],
        created_by=user_id,
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        images=[],
    )


async def get_datasets_by_user_id(
    db: AsyncIOMotorDatabase, user_id: UUID
) -> list[Dataset]:
    if not validate_user(user_id):
        raise ValueError("User not found")

    collection = db["datasets"]
    user_id_binary = bson.Binary.from_uuid(user_id)
    result = await collection.find({"user_id": user_id_binary}).to_list(length=None)
    datasets = [
        Dataset(
            id=doc["id"],
            name=doc["name"],
            created_by=doc["user_id"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            images=doc["images"],
        )
        for doc in result
    ]
    return datasets
