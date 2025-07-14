from functools import cached_property
from typing import Optional
from uuid import UUID

import strawberry
from core import auth
from fastapi import FastAPI
from strawberry.fastapi import BaseContext, GraphQLRouter


@strawberry.type
class User:
    id: UUID
    clerk_id: str


class Context(BaseContext):
    @cached_property
    def user(self) -> Optional[User]:
        if not self.request:
            return None
        try:
            token = self.request.headers.get("Authorization", None)
            if not token:
                return None
            token = token.split(" ")[1]
            user_id, clerk_id = auth.get_current_user_from_token(token)
            return User(id=user_id, clerk_id=clerk_id)
        except Exception as e:
            print(e)
            return None


def get_context() -> Context:
    return Context()
