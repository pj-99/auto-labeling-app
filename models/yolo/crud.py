import os
from datetime import datetime
from typing import List
from uuid import UUID

from data_types import LabelDetectionByYOLO
from pymongo import AsyncMongoClient

client = AsyncMongoClient(os.getenv("MONGO_URL"), uuidRepresentation="standard")


async def get_dataset_class_name_to_id(dataset_id: UUID):
    """Get the dataset's class name to id map

    Args:
        dataset_id (UUID)

    Returns:
        classes(dict): key is the class name, value is class id in DB
    """
    database = client.get_database("app")
    collection = database["datasets"]
    dataset = await collection.find_one({"id": dataset_id}, {"classes": 1, "_id": 0})
    classes = {item["name"]: item["id"] for item in dataset["classes"]}
    return classes


async def get_image_urls_and_ids(dataset_id: UUID):
    database = client.get_database("app")
    dataset = await database["datasets"].find_one(
        {"id": dataset_id}, {"_id": 0, "images": 1}
    )
    image_ids = dataset["images"]
    images = (
        await database["images"]
        .find({"id": {"$in": image_ids}}, {"image_url": 1, "_id": 0})
        .to_list()
    )

    image_urls = [image["image_url"] for image in images]
    return image_urls, image_ids


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
