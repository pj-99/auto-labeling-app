import enum
import json
from contextlib import asynccontextmanager
from typing import Annotated, List, Union
from uuid import UUID

import strawberry
from crud import create_job
from events import DatasetPredictEvent, ImagePredictEvent, SAMPredictEvent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model.auto_label_job import AutoLabelModel
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
class PredictJobCreatedSuccess:
    job_id: UUID


@strawberry.type
class PredictJobError:
    message: str


PredictJobResponse = Annotated[
    Union[PredictJobCreatedSuccess, PredictJobError],
    strawberry.union("PredictResponse"),
]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def predictSAM(
        self, image_url: str, points: List[List[List[int]]], labels: List[List[int]]
    ) -> PredictResult:
        resp = await nats_client.request(
            "predict.image.sam",
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

    @strawberry.mutation
    async def predictYoloOnDataset(
        self, dataset_id: UUID, user_id: UUID
    ) -> PredictJobResponse:
        return await sendPredictJob(
            dataset_id=dataset_id,
            user_id=user_id,
            model=AutoLabelModel.YOLO_WORLD,
        )

    @strawberry.mutation
    async def predictYoloOnImage(
        self, image_id: UUID, user_id: UUID
    ) -> PredictJobResponse:
        return await sendPredictJob(
            image_id=image_id,
            user_id=user_id,
            model=AutoLabelModel.YOLO_WORLD,
        )


async def sendPredictJob(
    user_id: UUID,
    model: AutoLabelModel,
    image_id: UUID = None,
    dataset_id: UUID = None,
):
    # Create the job in db
    try:
        job_id = await create_job(user_id, model, dataset_id=dataset_id)
    except Exception as e:
        print(e)
        return PredictJobError(message="Job cannot be created")

    # Set predict type that will be used in topic
    predic_type = "image" if image_id else "dataset"

    # Set method string that will be used in topic
    method = "yolo" if model == AutoLabelModel.YOLO_WORLD else "sam"

    # Send the job to broker
    try:
        if predic_type == "dataset":
            # Predict on the whole dataset
            await nats_client.publish(
                f"predict.{predic_type}.{method}",
                DatasetPredictEvent(dataset_id=dataset_id, job_id=job_id)
                .model_dump_json()
                .encode(),
            )
        else:
            # Predict on the single image
            await nats_client.publish(
                f"predict.{predic_type}.{method}",
                ImagePredictEvent(image_id=image_id, job_id=job_id)
                .model_dump_json()
                .encode(),
            )
    except Exception as e:
        print(e)
        # TODO: retry?
        return PredictJobError(message="Job cannot be sent to worker")

    return PredictJobCreatedSuccess(job_id=job_id)


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
