import asyncio
import json
import os

import nats
from events import TriggerDatasetPredictEvent
from handler import handle_predict_dataset
from nats.aio.client import Client

servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")


async def main():
    nc: Client = await nats.connect(servers)

    sub = await nc.subscribe("predict.dataset.yolo")

    # Handle incoming messages
    async for msg in sub.messages:
        event = TriggerDatasetPredictEvent.model_validate_json(msg.data)
        await handle_predict_dataset(event.dataset_id, event.job_id)

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
