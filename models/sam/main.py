import asyncio
import json
import os
import signal

import nats
from events import SAMPredictEvent
from nats.aio.client import Client
from predictor import InferenceAPI

servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")
inference_api = InferenceAPI()


async def main():
    nc: Client = await nats.connect(servers)

    sub = await nc.subscribe("sam.predict")

    # Handle incoming messages
    async for msg in sub.messages:
        event = SAMPredictEvent.model_validate_json(msg.data)
        print("Received event:")
        print(event)

        results = inference_api.predict([event.image_url], event.points, event.labels)

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

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
