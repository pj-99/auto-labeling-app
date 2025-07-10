import asyncio
import os
from datetime import datetime
from typing import List
from uuid import UUID

from data_types import LabelDetectionByYOLO
from pymongo import AsyncMongoClient

client = AsyncMongoClient(os.getenv("MONGO_URL"), uuidRepresentation="standard")


async def get_dataset_info(dataset_id: UUID):
    """Get the dataset's class name to id map

    Args:
        dataset_id (UUID)

    Returns:
        tuple: (class_name_to_id(dict), image_urls(list), image_ids(list))
    """
    database = client.get_database("app")
    pipeline = [
        {"$match": {"id": dataset_id}},
        # Join with collection of images
        {
            "$lookup": {
                "from": "images",
                "localField": "images",
                "foreignField": "id",
                "as": "image_mapping",
            },
        },
        {
            "$project": {
                "_id": 0,
                "classes": 1,
                "images": 1,
                "image_mapping.id": 1,
                "image_mapping.image_url": 1,
            }
        },
    ]
    result = await database["datasets"].aggregate(pipeline=pipeline)
    result = await result.to_list(1)

    if not result or len(result) == 0:
        raise ValueError(f"Dataset {dataset_id} not found")

    dataset_data = result[0]

    class_name_to_id = {item["name"]: item["id"] for item in dataset_data["classes"]}

    image_id_to_url = {
        img["id"]: img["image_url"] for img in dataset_data["image_mapping"]
    }
    image_ids = dataset_data["images"]
    image_urls = [image_id_to_url[image_id] for image_id in image_ids]
    return class_name_to_id, image_urls, image_ids


async def insert_label_detections(labels: List[LabelDetectionByYOLO]):
    database = client.get_database("app")
    collection = database["label_detections"]
    await collection.insert_many([label.model_dump() for label in labels])


async def set_job_done(job_id: UUID):
    database = client.get_database("app")
    collection = database["autolabel_jobs"]
    await collection.find_one_and_update(
        {"id": job_id}, {"$set": {"status": "done", "updated_at": datetime.now()}}
    )


async def set_job_failed(job_id: UUID):
    database = client.get_database("app")
    collection = database["autolabel_jobs"]
    await collection.find_one_and_update(
        {"id": job_id}, {"$set": {"status": "failed", "updated_at": datetime.now()}}
    )
