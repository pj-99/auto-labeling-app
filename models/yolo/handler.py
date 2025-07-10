import traceback
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from crud import get_dataset_info, insert_label_detections, set_job_done, set_job_failed
from data_types import LabelDetectionByYOLO
from predictor import InferenceAPI


async def handle_predict_dataset(dataset_id: UUID, job_id: UUID):
    """Handle auto labeling per dataset"""
    try:
        inference_api = InferenceAPI()

        class_name_to_id, image_urls, image_ids = await get_dataset_info(dataset_id)
        classes = list(class_name_to_id.keys())
        results = inference_api.predict(image_urls, classes)

        labels: List[LabelDetectionByYOLO] = []
        for image_idx, result in enumerate(results):
            if result.boxes is not None:
                for i, xywhn in enumerate(result.boxes.xywhn):
                    xywhn = xywhn.tolist()
                    cls_name = classes[int(result.boxes.cls[i].item())]
                    conf = result.boxes.conf[i].item()
                    label = LabelDetectionByYOLO(
                        id=uuid4(),
                        dataset_id=dataset_id,
                        image_id=image_ids[image_idx],
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

        # Save back to DB
        await insert_label_detections(labels)
        await set_job_done(job_id=job_id)
        print(f"Job: {job_id} is doned")
    except Exception as e:
        traceback.print_exc()
        print(f"Job: {job_id} is failed, {e}")
        await set_job_failed(job_id=job_id)


async def handle_predict_image(image_id: UUID, job_id: UUID):
    return
