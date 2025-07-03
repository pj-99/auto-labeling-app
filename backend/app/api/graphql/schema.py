import datetime
import typing
from uuid import UUID

import strawberry


@strawberry.type
class Image:
    id: UUID
    image_name: str
    image_url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    caption: str = ""
    created_by: UUID


@strawberry.type
class Dataset:
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    images: typing.List[Image]
