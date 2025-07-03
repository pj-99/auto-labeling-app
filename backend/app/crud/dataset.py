from datetime import datetime
from uuid import UUID, uuid4

import bson
from api.graphql.schema import Dataset
from motor.motor_asyncio import AsyncIOMotorDatabase


def validate_user_exist(user_id: UUID) -> bool:
    # TODO: validate user exist
    return True


async def create_dataset(db: AsyncIOMotorDatabase, user_id: UUID, name: str) -> Dataset:
    if not validate_user_exist(user_id):
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
    if not validate_user_exist(user_id):
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
