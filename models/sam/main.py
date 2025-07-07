from typing import List

import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from predictor import InferenceAPI
from strawberry.fastapi import GraphQLRouter

inference_api = InferenceAPI()


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
    def predict(
        self, image_url: str, points: List[List[int]], labels: List[int]
    ) -> PredictResult:
        results = inference_api.predict(image_url, points, labels)
        if len(results) == 0:
            raise Exception("No results found")
        result = results[0]

        return PredictResult(
            boxes=[Box(xyxy=box.xyxy.flatten().tolist()) for box in result.boxes],
            masks=[
                Mask(xy=coords.tolist())
                for result in results
                for coords in result.masks.xy
            ],
        )


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello, World!"


app = FastAPI()


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
