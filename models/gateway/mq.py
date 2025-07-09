import os

import nats


async def create_nats_client():
    servers = os.environ.get("NATS_URL", "nats://nats:4222").split(",")
    return await nats.connect(servers)
