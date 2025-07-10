from typing import List

from ultralytics import YOLOWorld
from ultralytics.engine.results import Results


class InferenceAPI:

    def __init__(self):
        self.model = YOLOWorld("yolov8s-worldv2.pt")
        print(self.model.info())

    def predict(self, image_paths: List[str], classes: List[str]) -> Results:
        print("Starting inferences...")
        self.model.set_classes(classes)
        results = self.model.predict(image_paths)
        return results
