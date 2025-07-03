from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.schema import Dataset, Image
from crud.dataset import create_class, create_dataset, insert_image_to_dataset
from motor.motor_asyncio import AsyncIOMotorDatabase


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_dataset(self, user_id: UUID, name: str) -> Dataset:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await create_dataset(db, user_id, name)

    @strawberry.mutation
    async def insert_image_to_dataset(
        self, user_id: UUID, dataset_id: UUID, image_url: str, image_name: str
    ) -> Image:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await insert_image_to_dataset(
            db, user_id, dataset_id, image_url, image_name
        )

    # @strawberry.mutation
    # async def create_class(self, dataset_id: UUID, name: str) -> Class:
    #     db: AsyncIOMotorDatabase = await anext(get_db())
    #     return await create_class(db, dataset_id, name)
