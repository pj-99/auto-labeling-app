from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LabelDetectionByYOLO(BaseModel):
    id: UUID
    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float
    conf: float
    dataset_id: UUID
    image_id: UUID
    generated_by: str = "YOLO"
    created_at: datetime
    updated_at: datetime
