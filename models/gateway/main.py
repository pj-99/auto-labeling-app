import json
from contextlib import asynccontextmanager
from typing import List

import strawberry
from events import SAMPredictEvent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mq import create_nats_client
from nats.aio.client import Client
from strawberry.fastapi import GraphQLRouter

nats_client: Client = None


@strawberry.type
class Box:
    xyxy: List[float]


@strawberry.type
class Mask:
    xy: List[List[float]]


@strawberry.type
class PredictResult:
    boxes: List[Box]
    masks: List[Mask]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def predictSAM(
        self, image_url: str, points: List[List[List[int]]], labels: List[List[int]]
    ) -> PredictResult:
        resp = await nats_client.request(
            "sam.predict",
            SAMPredictEvent(image_url=image_url, points=points, labels=labels)
            .model_dump_json()
            .encode(),
            timeout=10,
        )

        result = json.loads(resp.data.decode("utf-8"))

        return PredictResult(
            boxes=[Box(xyxy=box) for box in result["boxes"]],
            masks=[Mask(xy=mask) for mask in result["masks"]],
        )


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, World!"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global nats_client
    nats_client = await create_nats_client()
    yield
    await nats_client.drain()


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema=schema)

app.include_router(graphql_app, prefix="/graphql")
