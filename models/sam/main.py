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

    async def predict_handler(msg):
        event = SAMPredictEvent.model_validate_json(msg.data)
        print("Received event:")
        print(event)

        results = inference_api.predict(event.image_url, event.points, event.labels)

        if len(results) == 0:
            raise Exception("No results found")

        result = results[0]

        reply = {
            "boxes": [box.xyxy.flatten().tolist() for box in result.boxes],
            "masks": [
                coords.tolist() for result in results for coords in result.masks.xy
            ],
        }
        await msg.respond(json.dumps(reply).encode("utf-8"))

    sub = await nc.subscribe("sam.predict", cb=predict_handler)

    await nc.flush()

    stop_event = asyncio.Event()

    def signal_handler():
        print("SIGINT or SIGTERM received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)

    await stop_event.wait()
    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
