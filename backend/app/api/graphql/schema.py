import typing
from uuid import UUID

import strawberry
from models.dataset import Dataset as DatasetModel
from models.image import Image as ImageModel
from models.label_detection import LabelDetection as LabelDetectionModel
from models.label_segmentation import LabelSegmentation as LabelSegmentationModel
from models.object_class import Class as ClassModel
from models.user import User as UserModel


@strawberry.experimental.pydantic.type(model=ImageModel, all_fields=True)
class Image:
    pass


@strawberry.experimental.pydantic.type(model=ClassModel, all_fields=True)
class Class:
    pass


@strawberry.experimental.pydantic.type(model=DatasetModel, all_fields=True)
class Dataset:
    pass


@strawberry.experimental.pydantic.type(model=LabelDetectionModel, all_fields=True)
class LabelDetection:
    pass


@strawberry.experimental.pydantic.type(model=LabelSegmentationModel, all_fields=True)
class LabelSegmentation:
    pass


@strawberry.experimental.pydantic.type(model=UserModel, all_fields=True)
class User:
    pass
