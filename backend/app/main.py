import strawberry
from api.graphql.mutation import Mutation
from api.graphql.queries import Query
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

app = FastAPI()

app.include_router(graphql_app, prefix="/graphql")
