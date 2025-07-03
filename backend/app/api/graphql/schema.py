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
