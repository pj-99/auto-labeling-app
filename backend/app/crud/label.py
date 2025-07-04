import uuid
from datetime import datetime
from typing import List
from uuid import UUID

import bson
from fastapi import HTTPException
from models.label_detection import LabelDetection, LabelDetectionInput
from models.label_segmentation import LabelSegmentation
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument


async def get_label_detections(
    db: AsyncIOMotorDatabase, dataset_id: UUID, image_id: UUID
) -> list[LabelDetection]:
    # Mock data
    return [
        LabelDetection(
            dataset_id=dataset_id,
            image_id=image_id,
            class_id=0,
            x_center=0.5,
            y_center=0.5,
            width=0.2,
            height=0.1,
        ),
        LabelDetection(
            dataset_id=dataset_id,
            image_id=image_id,
            class_id=1,
            x_center=0.3,
            y_center=0.9,
            width=0.4,
            height=0.3,
        ),
    ]


async def upsert_label_detections(
    db: AsyncIOMotorDatabase,
    dataset_id: UUID,
    image_id: UUID,
    label_detections: List[LabelDetectionInput],
) -> List[LabelDetection]:
    collection = db["label_detections"]
    result = []
    labels_data = [
        {**label.model_dump(), "dataset_id": dataset_id, "image_id": image_id}
        for label in label_detections
    ]
    # Each label is a document
    for label in labels_data:
        if label["id"] is not None:
            # Update the label
            label["updated_at"] = datetime.now()
            res = await collection.find_one_and_update(
                {"id": label["id"]},
                {"$set": label},
                return_document=ReturnDocument.AFTER,
            )
            if res is None:
                raise ValueError("Label id provided not found")
            result.append(LabelDetection(**res))
        else:
            # Insert the label
            label["id"] = uuid.uuid4()
            label["created_at"] = datetime.now()
            label["updated_at"] = datetime.now()
            await collection.insert_one(label)
            result.append(LabelDetection(**label))
    return result


async def delete_label_detections(db: AsyncIOMotorDatabase, label_id: UUID) -> bool:
    collection = db["label_detections"]
    res = await collection.delete_one({"id": label_id})
    return res.deleted_count > 0


async def get_label_segmentations(
    db: AsyncIOMotorDatabase, dataset_id: UUID, image_id: UUID
) -> LabelSegmentation:
    pass
