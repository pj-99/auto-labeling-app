from typing import List
from uuid import UUID

from pydantic import BaseModel


class TriggerImagePredictEvent(BaseModel):
    """
    Trigger YOLO model to predict an image.
    """

    image_url: str
    classes: List[str]


class TriggerDatasetPredictEvent(BaseModel):
    """
    Trigger YOLO model to predict all images in a dataset.
    """

    dataset_id: UUID
    job_id: UUID
