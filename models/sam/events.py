from typing import List

from pydantic import BaseModel


# TODO: this is defined twice
class SAMPredictEvent(BaseModel):
    image_url: str
    points: List[List[List[int]]]
    labels: List[List[int]]
