from typing import List

from ultralytics import SAM
from ultralytics.engine.results import Results


class InferenceAPI:

    def __init__(self):
        self.model = SAM("sam2.1_t.pt")
        print(self.model.info())

    def predict(
        self, image_path: str, points: List[List[List[int]]], labels: List[List[int]]
    ) -> Results:
        results = self.model.predict(
            image_path,
            points=points,
            labels=labels,
        )
        return results
