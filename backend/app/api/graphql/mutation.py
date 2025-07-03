from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.schema import Dataset
from crud.dataset import create_dataset
from motor.motor_asyncio import AsyncIOMotorDatabase


@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_dataset(self, user_id: UUID, name: str) -> Dataset:
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await create_dataset(db, user_id, name)
