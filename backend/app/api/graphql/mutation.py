from typing import Annotated, List, Tuple, Union
from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.schema import (
    Class,
    Dataset,
    Image,
    LabelDetection,
    LabelSegmentation,
    User,
)
from clerk_backend_api import Clerk
from core.config import Settings
from crud.dataset import (
    create_dataset,
    delete_class,
    insert_class,
    insert_image_to_dataset,
)
from crud.label import (
    delete_label_detections,
    delete_label_segmentations,
    upsert_label_detections,
    upsert_label_segmentations,
)
from crud.user import create_user_if_not_exists
from models.dataset import TrainingType
from models.label_detection import LabelDetectionInput as LabelDetectionInputModel
from models.label_segmentation import (
    LabelSegmentationInput as LabelSegmentationInputModel,
)
from motor.motor_asyncio import AsyncIOMotorDatabase


@strawberry.type
class UpsertLabelDetectionSuccess:
    success: bool = True
    labels: List[LabelDetection]


@strawberry.type
class UpsertLabelSegmentationSuccess:
    success: bool = True
    labels: List[LabelSegmentation]


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
    async def login(self, clerk_user_id: str) -> User:
        db: AsyncIOMotorDatabase = await anext(get_db())

        isNewUser, user = await create_user_if_not_exists(db, clerk_user_id)
        if isNewUser:
            # Set the external_id in the clerk
            settings = Settings()
            async with Clerk(bearer_auth=settings.CLERK_SECRET_KEY) as clerk:
                await clerk.users.update_async(
                    user_id=clerk_user_id, external_id=str(user.id)
                )
        return user

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
        width: int,
        height: int,
    ) -> Image:

        if image_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise ValueError("Invalid image type")

        db: AsyncIOMotorDatabase = await anext(get_db())
        return await insert_image_to_dataset(
            db,
            user_id,
            dataset_id,
            gcs_file_name,
            image_name,
            image_type,
            width,
            height,
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

    @strawberry.input
    class LabelSegmentationInputGraphql:
        id: UUID | None = None
        class_id: int
        mask: List[float]

    @strawberry.mutation
    async def upsert_label_detections(
        self,
        dataset_id: UUID,
        image_id: UUID,
        label_detections: List[LabelDetectionInputGraphql],
    ) -> Annotated[
        Union[UpsertLabelDetectionSuccess, UpsertLabelError],
        strawberry.union("UpsertDetectionResponse"),
    ]:
        try:
            db: AsyncIOMotorDatabase = await anext(get_db())
            model_label_detections = [
                LabelDetectionInputModel(**label.__dict__) for label in label_detections
            ]
            result = await upsert_label_detections(
                db, dataset_id, image_id, label_detections=model_label_detections
            )
            return UpsertLabelDetectionSuccess(labels=result)
        except Exception as e:
            print(e)
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
        except Exception as e:
            print(e)
            return DeleteLabelError(
                message="delete label failed", code="INTERNAL_SERVER_ERROR"
            )

    @strawberry.mutation
    async def upsert_label_segmentations(
        self,
        dataset_id: UUID,
        image_id: UUID,
        label_segmentations: List[LabelSegmentationInputGraphql],
    ) -> Annotated[
        Union[UpsertLabelSegmentationSuccess, UpsertLabelError],
        strawberry.union("UpsertSegmentationResponse"),
    ]:
        try:
            db: AsyncIOMotorDatabase = await anext(get_db())
            labels = [
                LabelSegmentationInputModel(**label.__dict__)
                for label in label_segmentations
            ]
            result = await upsert_label_segmentations(
                db, dataset_id, image_id, label_segmentations=labels
            )
            return UpsertLabelSegmentationSuccess(labels=result)
        except Exception as e:
            # This can be enhanced
            print(e)
            return UpsertLabelError(
                message="upsert label detections failed", code="INTERNAL_SERVER_ERROR"
            )

    @strawberry.mutation
    async def delete_label_segmentations(self, label_id: UUID) -> Annotated[
        Union[DeleteLabelSuccess, DeleteLabelError],
        strawberry.union("DeleteLabelResponse"),
    ]:
        try:
            db: AsyncIOMotorDatabase = await anext(get_db())
            deleted = await delete_label_segmentations(db, label_id)
            if deleted:
                return DeleteLabelSuccess(success=True)
            else:
                return DeleteLabelError(
                    message="delete label not found",
                    code="NOT_FOUND",
                )
        except Exception as e:
            print(e)
            return DeleteLabelError(
                message="delete label failed", code="INTERNAL_SERVER_ERROR"
            )
