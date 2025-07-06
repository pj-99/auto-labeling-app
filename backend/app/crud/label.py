import uuid
from datetime import datetime
from typing import List, Type, TypeVar
from uuid import UUID

import bson
from fastapi import HTTPException
from models.label_detection import LabelDetection, LabelDetectionInput
from models.label_segmentation import LabelSegmentation, LabelSegmentationInput
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

T = TypeVar("T", LabelDetection, LabelSegmentation)
InputT = TypeVar("inputT", LabelDetectionInput, LabelSegmentationInput)


# The generic type method for upserting label of detection or segmentation
async def upsert_label(
    db: AsyncIOMotorDatabase,
    dataset_id: UUID,
    image_id: UUID,
    labels: List[InputT],
    output_models: Type[T],
    collection_name: str,
) -> List[T]:
    collection = db[collection_name]
    result = []
    labels_data = [
        {**label.model_dump(), "dataset_id": dataset_id, "image_id": image_id}
        for label in labels
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
            result.append(output_models(**res))
        else:
            # Insert the label
            label["id"] = uuid.uuid4()
            label["created_at"] = datetime.now()
            label["updated_at"] = datetime.now()
            await collection.insert_one(label)
            result.append(output_models(**label))
    return result


async def get_label_detections(
    db: AsyncIOMotorDatabase, dataset_id: UUID, image_id: UUID
) -> list[LabelDetection]:
    collection = db["label_detections"]
    res = await collection.find(
        {"dataset_id": dataset_id, "image_id": image_id}
    ).to_list(length=None)
    print("label count", len(res))
    return [LabelDetection(**label) for label in res]


async def upsert_label_detections(
    db: AsyncIOMotorDatabase,
    dataset_id: UUID,
    image_id: UUID,
    label_detections: List[LabelDetectionInput],
) -> List[LabelDetection]:
    return await upsert_label(
        db, dataset_id, image_id, label_detections, LabelDetection, "label_detections"
    )


async def delete_label_detections(db: AsyncIOMotorDatabase, label_id: UUID) -> bool:
    collection = db["label_detections"]
    res = await collection.delete_one({"id": label_id})
    return res.deleted_count > 0


# Label Segmentation
async def get_label_segmentations(
    db: AsyncIOMotorDatabase, dataset_id: UUID, image_id: UUID
) -> LabelSegmentation:
    collection = db["label_segmentations"]
    res = await collection.find(
        {"dataset_id": dataset_id, "image_id": image_id}
    ).to_list(length=None)
    print("label count", len(res))
    return [LabelSegmentation(**label) for label in res]


async def upsert_label_segmentations(
    db: AsyncIOMotorDatabase,
    dataset_id: UUID,
    image_id: UUID,
    label_segmentations: List[LabelSegmentationInput],
) -> List[LabelSegmentation]:
    return await upsert_label(
        db,
        dataset_id,
        image_id,
        label_segmentations,
        LabelSegmentation,
        "label_segmentations",
    )
