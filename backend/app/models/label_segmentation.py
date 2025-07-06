from datetime import datetime
from typing import List, Tuple
from uuid import UUID

from models.label import LabelBase


class LabelSegmentationBase(LabelBase):
    """
    The core data of segmentation
    """

    mask: List[float]


# This define two time
# Maybe it can be improved but need to check strawberry docs
class LabelSegmentationInput(LabelSegmentationBase):
    id: UUID | None = None


class LabelSegmentation(LabelSegmentationBase):
    id: UUID | None = None
    dataset_id: UUID
    image_id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
