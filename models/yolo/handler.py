import traceback
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from crud import (
    get_dataset_info,
    get_image_info,
    insert_label_detections,
    set_job_done,
    set_job_failed,
)
from data_types import LabelDetectionByYOLO
from predictor import InferenceAPI


async def handle_predict_dataset(dataset_id: UUID, job_id: UUID):
    """Handle auto labeling for dataset"""
    try:
        class_name_to_id, image_urls, image_ids = await get_dataset_info(dataset_id)
        classes = list(class_name_to_id.keys())

        inference_api = InferenceAPI()
        results = inference_api.predict(image_urls, classes)

        labels: List[LabelDetectionByYOLO] = []
        for image_idx, result in enumerate(results):
            image_id = image_ids[image_idx]
            labels.extend(
                result_to_labels(
                    result=result,
                    dataset_id=dataset_id,
                    image_id=image_id,
                    class_name_to_id=class_name_to_id,
                    classes=classes,
                )
            )

        # Save back to DB
        await insert_label_detections(labels)
        await set_job_done(job_id=job_id)
        print(f"Job: {job_id} is doned")
    except Exception as e:
        traceback.print_exc()
        print(f"Job: {job_id} is failed, {e}")
        await set_job_failed(job_id=job_id)


async def handle_predict_image(image_id: UUID, dataset_id: UUID, job_id: UUID):
    """Handle auto labeling for image"""
    try:
        # Get required data(image_url, class_ids)
        class_name_to_id, image_url = await get_image_info(
            dataset_id=dataset_id, image_id=image_id
        )
        classes = list(class_name_to_id.keys())
        inference_api = InferenceAPI()
        results = inference_api.predict([image_url], classes)
        if len(results) == 0:
            raise ValueError("Prediction return no result")
        result = results[0]
        labels = result_to_labels(
            result=result,
            classes=classes,
            dataset_id=dataset_id,
            image_id=image_id,
            class_name_to_id=class_name_to_id,
        )

        # Save back to DB
        await insert_label_detections(labels)
        await set_job_done(job_id=job_id)
        print(f"Job: {job_id} is doned")

    except Exception as e:
        traceback.print_exc()
        print(f"Job: {job_id} is failed, {e}")
        await set_job_failed(job_id=job_id)


def result_to_labels(
    result, classes, dataset_id, image_id, class_name_to_id
) -> List[LabelDetectionByYOLO]:
    """Convert the prediction result into label"""
    labels = []
    if result.boxes:
        for i, xywhn in enumerate(result.boxes.xywhn):
            xywhn = xywhn.tolist()
            cls_name = classes[int(result.boxes.cls[i].item())]
            conf = result.boxes.conf[i].item()
            label = LabelDetectionByYOLO(
                id=uuid4(),
                dataset_id=dataset_id,
                image_id=image_id,
                class_id=class_name_to_id[cls_name],
                x_center=xywhn[0],
                y_center=xywhn[1],
                width=xywhn[2],
                height=xywhn[3],
                conf=conf,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            labels.append(label)
    return labels
