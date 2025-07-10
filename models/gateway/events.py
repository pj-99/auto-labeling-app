from typing import List
from uuid import UUID

from pydantic import BaseModel


class SAMPredictEvent(BaseModel):
    image_url: str
    points: List[List[List[int]]]
    labels: List[List[int]]


class DatasetPredictEvent(BaseModel):
    """
    Trigger a job predicting all the images in the dataset.
    """

    dataset_id: UUID
    job_id: UUID


class ImagePredictEvent(BaseModel):
    """
    Trigger a job predicting an image.
    """

    image_id: UUID
    job_id: UUID
