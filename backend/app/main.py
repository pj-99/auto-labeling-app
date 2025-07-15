import os

import strawberry
from api.graphql.context import get_context
from api.graphql.mutation import Mutation
from api.graphql.queries import Query
from api.image_upload.image_upload import GenerateSignedUrlRequest, generate_signed_url
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL")],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "frontend_url": os.getenv("FRONTEND_URL"),
        "cors_origins": ["http://localhost:3000", os.getenv("FRONTEND_URL")],
    }


@app.post("/generate-signed-url")
def get_signed_url(req: GenerateSignedUrlRequest):
    result = generate_signed_url(req.content_type)
    return result


app.include_router(graphql_app, prefix="/graphql")
