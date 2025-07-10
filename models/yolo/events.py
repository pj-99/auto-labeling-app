from uuid import UUID

from pydantic import BaseModel


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
    dataset_id: UUID
