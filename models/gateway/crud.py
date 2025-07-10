import os
import uuid
from typing import Union
from uuid import UUID, uuid4

from model.auto_label_job import AutoLabelModel, JobStatus
from pymongo import AsyncMongoClient

client = AsyncMongoClient(os.getenv("MONGO_URL"), uuidRepresentation="standard")


async def create_job(
    user_id: UUID,
    model: AutoLabelModel,
    dataset_id: Union[UUID, None] = None,
    image_id: Union[UUID, None] = None,
):
    database = client.get_database("app")
    collection = database["autolabel_jobs"]
    job_id = uuid4()

    doc = {
        "id": job_id,
        "user_id": user_id,
        "status": JobStatus.CREATED.value,
        "model": model.value,
    }

    if dataset_id:
        doc["dataset_id"] = dataset_id

    if image_id:
        doc["image_id"] = image_id

    await collection.insert_one(doc)

    return job_id
