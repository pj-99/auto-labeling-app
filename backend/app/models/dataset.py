from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel

from .image import Image
from .object_class import Class


class TrainingType(Enum):
    DETECT = "detect"
    SEGMENT = "segment"


class Dataset(BaseModel):
    id: UUID
    name: str
    training_type: TrainingType = TrainingType.DETECT
    images: List[Image] = []
    classes: List[Class] = []
    created_by: UUID
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
