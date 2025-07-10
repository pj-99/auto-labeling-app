import asyncio
import json
import os
from typing import List

import nats
from events import SAMPredictEvent
from nats.aio.client import Client
from predictor import InferenceAPI
from ultralytics.utils import ThreadingLocked

servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")

inference_api = InferenceAPI()


@ThreadingLocked()
def thread_safe_predict(
    image_paths: List[str],
    points: List[List[List[int]]],
    labels: List[List[int]],
):
    results = inference_api.predict(image_paths, points, labels)
    return results


async def main():
    nc: Client = await nats.connect(servers)

    sub = await nc.subscribe("predict.image.sam")

    # Handle incoming messages
    async for msg in sub.messages:
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
        except Exception as e:
            await msg.respond(json.dumps({"error": str(e)}).encode("utf-8"))

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
