from typing import List, OrderedDict, Union

import cv2
import numpy as np
import torch
from ultralytics import SAM
from ultralytics.engine.results import Results
from ultralytics.models.sam import SAM2Predictor


class InferenceAPI:
    def __init__(self, model_path="sam2.1_t.pt"):
        self.model_path = model_path
        self.max_cache_predcitor_size = 10
        # Preload
        print(SAM(model_path).info())

        # LRU cache
        self.sessions: OrderedDict[str, SAM2Predictor] = OrderedDict()

    def _get_or_create_predictor(
        self, image_path: Union[str, List[str]]
    ) -> SAM2Predictor:
        # Normalize input to string
        if isinstance(image_path, list):
            if len(image_path) == 1:
                image_path = image_path[0]
            else:
                raise ValueError(
                    "Expected single image path, got list with multiple items"
                )

        if image_path in self.sessions:
            # Cache hit
            self.sessions.move_to_end(image_path)
            return self.sessions[image_path]
        else:
            overrides = dict(
                conf=0.99,
                task="segment",
                mode="predict",
                imgsz=1024,
                model=self.model_path,
            )
            predictor = SAM2Predictor(overrides=overrides)
            print(f"Loading model for image: {image_path}")

            # Download image from URL or load from local path
            if image_path.startswith(("http://", "https://")):
                import requests

                try:
                    response = requests.get(image_path, timeout=30)
                    response.raise_for_status()
                    image_array = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    print(f"Successfully downloaded image from URL: {image_path}")
                except Exception as e:
                    raise ValueError(
                        f"Failed to download image from URL {image_path}: {str(e)}"
                    )
            else:
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Could not load local image from: {image_path}")

            if image is None:
                raise ValueError(f"Could not decode image from: {image_path}")

            predictor.set_image(image)

            # Prevent memory leak
            if len(self.sessions) >= self.max_cache_predcitor_size:
                self.sessions.popitem(last=False)
            self.sessions[image_path] = predictor
            return predictor

    def predict(
        self,
        image_path: List[str],
        points: List[List[List[int]]],
        labels: List[List[int]],
    ) -> List[Results]:
        print(f"Predicting for image: {image_path}")
        predictor = self._get_or_create_predictor(image_path[0])
        results = predictor(points=points, labels=labels)
        return self._filter_mask_by_point(
            results, points[0][0]
        )  # Use the first click point

    def _filter_mask_by_point(
        self,
        results: List[Results],
        point: List[int],  # [x, y]
        min_area_ratio: float = 0.05,
        nms_thresh: float = 0.7,
    ) -> List[Results]:
        """
        Selects the region from a multi-component mask that contains the click point,
        then removes small regions using Ultralytics' built-in cleaning function.
        """
        if not results or results[0].masks is None:
            raise ValueError("Empty results or missing masks")

        # Convert mask tensor to numpy binary format
        mask_tensor = results[0].masks.data[0]  # shape: [H, W]
        mask_np = (mask_tensor > 0.5).cpu().numpy().astype(np.uint8)

        # Decompose into connected components
        _, labeled = cv2.connectedComponents(mask_np)

        # Use (y, x) for OpenCV access
        px, py = point[0], point[1]
        component_id = labeled[py, px]

        if component_id == 0:
            raise ValueError("Point is not inside any component region.")

        # Create a mask for just the selected component
        selected_mask = (labeled == component_id).astype(np.uint8)
        selected_mask_tensor = torch.tensor(selected_mask).unsqueeze(0)  # [1, H, W]

        # Compute area and apply dynamic min_area threshold
        pixel_count = selected_mask.sum()
        min_area = int(pixel_count * min_area_ratio)

        # Clean using SAM utility
        cleaned_masks, _ = SAM2Predictor.remove_small_regions(
            masks=selected_mask_tensor, min_area=min_area, nms_thresh=nms_thresh
        )

        # Replace the original mask in the result
        results[0].masks.data = cleaned_masks
        return results
