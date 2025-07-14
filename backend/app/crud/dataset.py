from datetime import datetime
from typing import List, Union
from uuid import UUID, uuid4

import bson
from api.deps import settings
from models.dataset import Dataset, TrainingType
from models.image import Image
from models.object_class import Class
from motor.motor_asyncio import AsyncIOMotorDatabase


async def check_dataset_exists(db: AsyncIOMotorDatabase, dataset_id: UUID) -> bool:
    return await db["datasets"].find_one({"id": dataset_id}) is not None


async def insert_image_to_dataset(
    db: AsyncIOMotorDatabase,
    user_id: UUID,
    dataset_id: UUID,
    gcs_file_name: str,
    image_name: str,
    image_type: str,
    width: int,
    height: int,
) -> Image:
    if not await check_dataset_exists(db, dataset_id):
        raise ValueError("Dataset not found")

    try:
        image_url = f"https://storage.googleapis.com/{settings.GCP_STORAGE_BUCKET}/{gcs_file_name}"
        # Insert to images collection
        image_id = uuid4()

        image = Image(
            id=image_id,
            image_name=image_name,
            image_type=image_type,
            width=width,
            height=height,
            image_url=image_url,
            created_by=user_id,
        )
        image_dict = image.model_dump(mode="python")
        await db["images"].insert_one(image_dict)

        # Update the dataset collection
        await db["datasets"].update_one(
            {"id": bson.Binary.from_uuid(dataset_id)},
            {"$push": {"images": image_id}},
        )
        return image
    except Exception as e:
        raise e


async def create_dataset(
    db: AsyncIOMotorDatabase, user_id: UUID, name: str, training_type: TrainingType
) -> Dataset:

    collection = db["datasets"]
    new_dataset_id = uuid4()
    user_id_binary = bson.Binary.from_uuid(user_id)
    dataset_id_binary = bson.Binary.from_uuid(new_dataset_id)

    doc = {
        "id": dataset_id_binary,
        "user_id": user_id_binary,
        "name": name,
        "training_type": training_type.value,
        "images": [],
        "classes": [],
        "updated_at": datetime.now(),
        "created_at": datetime.now(),
    }
    await collection.insert_one(doc)
    return Dataset(
        id=new_dataset_id,
        name=doc["name"],
        created_by=user_id,
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        images=[],
        classes=[],
        training_type=TrainingType(doc["training_type"]),
    )


async def _get_dataset_with_images(
    db: AsyncIOMotorDatabase, dataset_id: UUID
) -> Union[Dataset, None]:
    """Get the image info of a dataset"""
    # TODO: this function and its caller can be replaced with a single query

    # 1. match datasets by id
    # 2. lookup join by images
    # 3. sort by created_at
    collection = db["datasets"]
    pipeline = [
        {"$match": {"id": dataset_id}},
        {
            "$lookup": {
                "from": "images",
                "foreignField": "id",
                "localField": "images",
                "as": "images",
            }
        },
        {"$sort": {"created_at": -1}},
    ]

    result = await collection.aggregate(pipeline).to_list(length=1)

    if not result or len(result) == 0:
        print(f"Dataset {dataset_id} not found")
        return None

    doc = result[0]
    images = doc.get("images", [])

    # Transform the result
    return Dataset(
        id=doc["id"],
        name=doc["name"],
        created_by=doc["user_id"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        images=images,
        training_type=(
            TrainingType(doc["training_type"])
            if "training_type" in doc
            else TrainingType.DETECT
        ),
    )


async def get_datasets_by_user_id(
    db: AsyncIOMotorDatabase, user_id: UUID
) -> list[Dataset]:
    collection = db["datasets"]
    user_id_binary = bson.Binary.from_uuid(user_id)
    result = (
        await collection.find({"user_id": user_id_binary})
        .sort("updated_at", -1)
        .to_list(length=None)
    )

    datasets = []
    for doc in result:
        images = []

        for image_uuid in doc["images"]:
            image = await db["images"].find_one(
                {"id": bson.Binary.from_uuid(image_uuid)}
            )

            if image:
                images.append(image)

        datasets.append(
            Dataset(
                id=doc["id"],
                name=doc["name"],
                created_by=doc["user_id"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                images=images,
                training_type=(
                    TrainingType(doc["training_type"])
                    if "training_type" in doc
                    else TrainingType.DETECT
                ),
            )
        )

    return datasets


async def insert_class(db: AsyncIOMotorDatabase, dataset_id: UUID, name: str) -> Class:
    if not await check_dataset_exists(db, dataset_id):
        raise ValueError("Dataset not found")

    dataset = await db["datasets"].find_one({"id": dataset_id})
    classes = dataset.get("classes", [])
    class_id = len(classes) + 1
    doc = {
        "id": class_id,
        "name": name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    await db["datasets"].update_one(
        {"id": dataset_id},
        {"$push": {"classes": doc}},
    )
    return Class(**doc)


async def delete_class(
    db: AsyncIOMotorDatabase, dataset_id: UUID, class_id: int
) -> bool:
    if not await check_dataset_exists(db, dataset_id):
        raise ValueError("Dataset not found")

    result = await db["datasets"].update_one(
        {"id": dataset_id},
        {"$pull": {"classes": {"id": class_id}}},
    )

    return result.modified_count > 0


async def get_classes_by_dataset_id(
    db: AsyncIOMotorDatabase, dataset_id: UUID
) -> Union[List[Class], None]:
    if not await check_dataset_exists(db, dataset_id):
        return None

    result = await db["datasets"].find_one({"id": dataset_id})
    if not result:
        return None

    classes = result.get("classes", [])
    return [Class(**cls) for cls in classes]


async def get_dataset(
    db: AsyncIOMotorDatabase, dataset_id: UUID, user_id: UUID
) -> Union[Dataset, None]:
    result = await _get_dataset_with_images(db, dataset_id)
    if not result:
        return None

    if result.created_by != user_id:
        print(f"User {user_id} does not have access to this dataset: {dataset_id}")
        return None

    return result
