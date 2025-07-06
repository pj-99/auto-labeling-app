from datetime import datetime
from uuid import UUID

from models.label import LabelBase


class LabelDetectionBase(LabelBase):
    x_center: float
    y_center: float
    width: float
    height: float


# This define two time
# Maybe it can be improved but need to check strawberry docs
class LabelDetectionInput(LabelDetectionBase):
    id: UUID | None = None


class LabelDetection(LabelDetectionBase):
    id: UUID | None = None
    dataset_id: UUID
    image_id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
