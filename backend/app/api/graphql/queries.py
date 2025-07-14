import typing
from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.context import Context
from api.graphql.schema import Class, Dataset, Image, LabelDetection, LabelSegmentation
from crud.dataset import get_classes_by_dataset_id, get_datasets_by_user_id
from crud.image import get_image
from crud.label import get_label_detections, get_label_segmentations
from motor.motor_asyncio import AsyncIOMotorDatabase
from strawberry.types import Info


@strawberry.type
class Query:
    @strawberry.field
    async def datasets(
        self, info: Info[Context], user_id: UUID
    ) -> typing.List[Dataset]:
        if not info.context.user:
            return []
        # TODO: think about this
        # Can we use dependency injection?
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_datasets_by_user_id(db, user_id)

    @strawberry.field
    async def image(self, user_id: UUID, image_id: UUID) -> Image:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_image(db, user_id, image_id)

    @strawberry.field
    async def classes(self, dataset_id: UUID) -> list[Class]:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_classes_by_dataset_id(db, dataset_id)

    @strawberry.field
    async def label_detections(
        self, dataset_id: UUID, image_id: UUID
    ) -> list[LabelDetection]:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_label_detections(db, dataset_id, image_id)

    @strawberry.field
    async def label_segmentations(
        self, dataset_id: UUID, image_id: UUID
    ) -> list[LabelSegmentation]:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_label_segmentations(db, dataset_id, image_id)
