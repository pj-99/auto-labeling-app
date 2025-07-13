import asyncio
import json
import os
from typing import List

import nats
from events import SAMPredictEvent
from predictor import InferenceAPI
from ultralytics.utils import ThreadingLocked

inference_api = InferenceAPI()


@ThreadingLocked()
def thread_safe_predict(
    image_paths: List[str],
    points: List[List[List[int]]],
    labels: List[List[int]],
):
    results = inference_api.predict(image_paths, points, labels)
    return results


async def handle_sam(msg):
    try:
        event = SAMPredictEvent.model_validate_json(msg.data)
        print("Received event:")
        print(event)

        results = thread_safe_predict(
            [event.image_url],
            event.points,
            event.labels,
        )

        boxes = []
        masks = []
        for result in results:
            if result.boxes is not None:
                boxes.append(result.boxes.xyxy.flatten().tolist())
            if result.masks is not None:
                curMask = []
                for segs in result.masks.xy:
                    for coords in segs:
                        curMask.append(coords.flatten().tolist())
                masks.append(curMask)

        reply = {
            "boxes": boxes,
            "masks": masks,
        }
        await msg.respond(json.dumps(reply).encode("utf-8"))
        print("Reply sent successfully")

    except Exception as e:
        print(f"Error processing message: {e}")
        await msg.respond(json.dumps({"error": str(e)}).encode("utf-8"))


async def main():
    servers = os.environ.get("NATS_URL", "nats://nats:4222").split(",")
    nats_client = await nats.connect(servers)

    print("Starting NATS subscriber...")
    await nats_client.subscribe("predict.image.sam", cb=handle_sam)
    await nats_client.flush()
    print("Subscribed to predict.image.sam")

    shutdown_event = asyncio.Event()

    try:
        await shutdown_event.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await nats_client.drain()


if __name__ == "__main__":
    asyncio.run(main())
