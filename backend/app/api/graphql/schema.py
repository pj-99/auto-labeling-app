import typing

import strawberry
from models.dataset import Dataset as DatasetModel
from models.image import Image as ImageModel
from models.object_class import Class as ClassModel


@strawberry.experimental.pydantic.type(model=ImageModel, all_fields=True)
class Image:
    pass


@strawberry.experimental.pydantic.type(model=ClassModel, all_fields=True)
class Class:
    pass


@strawberry.experimental.pydantic.type(model=DatasetModel, all_fields=True)
class Dataset:
    pass
    # id: strawberry.auto
    # name: strawberry.auto
    # images: typing.List[Image]
    # classes: strawberry.auto
    # created_by: strawberry.auto
    # created_at: strawberry.auto
    # updated_at: strawberry.auto
