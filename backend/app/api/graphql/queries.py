import typing
from uuid import UUID

import strawberry
from api.deps import get_db
from api.graphql.schema import Dataset
from crud.dataset import get_datasets_by_user_id
from motor.motor_asyncio import AsyncIOMotorDatabase
from strawberry.types import Info


@strawberry.type
class Query:
    @strawberry.field
    async def datasets(self, info: Info, user_id: UUID) -> typing.List[Dataset]:
        # TODO: think about this
        # Can we use dependency injection?
        db: AsyncIOMotorDatabase = await anext(get_db())
        return await get_datasets_by_user_id(db, user_id)
