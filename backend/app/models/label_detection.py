from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class LabelDetectionBase(BaseModel):
    class_id: int
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
