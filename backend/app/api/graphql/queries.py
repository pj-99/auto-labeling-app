import typing
from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.schema import Dataset, LabelDetection, LabelSegmentation
from crud.dataset import get_datasets_by_user_id
from crud.label import get_label_detections, get_label_segmentations
from motor.motor_asyncio import AsyncIOMotorDatabase


@strawberry.type
class Query:
    @strawberry.field
    async def datasets(self, user_id: UUID) -> typing.List[Dataset]:
        # TODO: think about this
        # Can we use dependency injection?
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_datasets_by_user_id(db, user_id)

    @strawberry.field
    async def label_detections(
        self, dataset_id: UUID, image_id: UUID
    ) -> list[LabelDetection]:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_label_detections(db, dataset_id, image_id)

    # @strawberry.field
    # async def label_segmentations(
    #     self, dataset_id: UUID, image_id: UUID
    # ) -> LabelSegmentation:
    #     db: AsyncIOMotorDatabase = await anext(get_db())
    #     return await get_label_segmentations(db, dataset_id, image_id)
