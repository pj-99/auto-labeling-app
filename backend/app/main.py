import strawberry
from api.graphql.mutation import Mutation
from api.graphql.queries import Query
from api.image_upload.image_upload import GenerateSignedUrlRequest, generate_signed_url
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate-signed-url")
def get_signed_url(req: GenerateSignedUrlRequest):
    result = generate_signed_url(req.content_type)
    return result


app.include_router(graphql_app, prefix="/graphql")
