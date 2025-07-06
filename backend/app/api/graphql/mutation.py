from typing import Annotated, List, Union
from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.schema import Class, Dataset, Image, LabelDetection
from crud.dataset import (
    create_dataset,
    delete_class,
    insert_class,
    insert_image_to_dataset,
)
from crud.label import delete_label_detections, upsert_label_detections
from models.dataset import TrainingType
from models.label_detection import LabelDetectionInput as LabelDetectionInputModel
from motor.motor_asyncio import AsyncIOMotorDatabase


@strawberry.type
class UpsertLabelSuccess:
    success: bool = True
    labels: List[LabelDetection]


@strawberry.type
class UpsertLabelError:
    message: str
    code: str


@strawberry.type
class DeleteLabelSuccess:
    success: bool = True


@strawberry.type
class DeleteLabelError:
    message: str
    code: str


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_dataset(
        self, user_id: UUID, name: str, training_type: TrainingType
    ) -> Dataset:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await create_dataset(db, user_id, name, training_type)

    @strawberry.mutation
    async def insert_image_to_dataset(
        self,
        user_id: UUID,
        dataset_id: UUID,
        gcs_file_name: str,
        image_name: str,
        image_type: str,
    ) -> Image:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await insert_image_to_dataset(
            db, user_id, dataset_id, gcs_file_name, image_name, image_type
        )

    @strawberry.mutation
    async def insert_class(self, dataset_id: UUID, name: str) -> Class:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await insert_class(db, dataset_id, name)

    @strawberry.mutation
    async def delete_class(self, dataset_id: UUID, class_id: int) -> bool:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await delete_class(db, dataset_id, class_id)

    @strawberry.input
    class LabelDetectionInputGraphql:
        id: UUID | None = None
        class_id: int
        x_center: float
        y_center: float
        width: float
        height: float

    @strawberry.mutation
    async def upsert_label_detections(
        self,
        dataset_id: UUID,
        image_id: UUID,
        label_detections: List[LabelDetectionInputGraphql],
    ) -> Annotated[
        Union[UpsertLabelSuccess, UpsertLabelError],
        strawberry.union("UpsertResponse"),
    ]:

        try:
            db: AsyncIOMotorDatabase = await anext(get_db())
            model_label_detections = [
                LabelDetectionInputModel(**label.__dict__) for label in label_detections
            ]
            result = await upsert_label_detections(
                db, dataset_id, image_id, label_detections=model_label_detections
            )
            return UpsertLabelSuccess(labels=result)
        except Exception:
            # This can be enhanced
            return UpsertLabelError(
                message="upsert label detections failed", code="INTERNAL_SERVER_ERROR"
            )

    @strawberry.mutation
    async def delete_label_detections(self, label_id: UUID) -> Annotated[
        Union[DeleteLabelSuccess, DeleteLabelError],
        strawberry.union("DeleteLabelResponse"),
    ]:
        try:
            db: AsyncIOMotorDatabase = await anext(get_db())
            deleted = await delete_label_detections(db, label_id)
            if deleted:
                return DeleteLabelSuccess(success=True)
            else:
                return DeleteLabelError(
                    message="delete label not found",
                    code="NOT_FOUND",
                )
        except Exception:
            return DeleteLabelError(
                message="delete label failed", code="INTERNAL_SERVER_ERROR"
            )
