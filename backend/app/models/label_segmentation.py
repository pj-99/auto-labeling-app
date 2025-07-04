from typing import List
from uuid import UUID

from pydantic import BaseModel


class LabelSegmentation(BaseModel):
    dataset_id: UUID
    image_id: UUID
    class_id: int
    segmentation: List[float]
