from typing import List

from pydantic import BaseModel


class SAMPredictEvent(BaseModel):
    image_url: str
    points: List[List[List[int]]]
    labels: List[List[int]]
