import asyncio
import os

import nats
from events import TriggerDatasetPredictEvent, TriggerImagePredictEvent
from handler import handle_predict_dataset
from nats.aio.client import Client
from nats.aio.msg import Msg

servers = os.environ.get("NATS_URL", "nats://localhost:4222").split(",")


async def main():
    nc: Client = await nats.connect(servers)

    await nc.subscribe("predict.dataset.yolo", cb=on_predict_dataset)

    await nc.subscribe("predict.image.yolo", cb=on_predict_dataset)

    print("All subscribed")

    shutdown_event = asyncio.Event()

    try:
        await shutdown_event.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await nc.drain()


async def on_predict_dataset(msg: Msg):
    event = TriggerDatasetPredictEvent.model_validate_json(msg.data)
    await handle_predict_dataset(event.dataset_id, event.job_id)


async def on_predict_image(msg: Msg):
    # TODO
    event = TriggerImagePredictEvent.model_validate_json(msg.data)


if __name__ == "__main__":
    asyncio.run(main())
