from functools import cached_property
from typing import Optional

from core import auth
from models.user import User
from strawberry.fastapi import BaseContext


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
            user_id, clerk_user_id = auth.get_current_user_from_token(token)
            return User(id=user_id, clerk_user_id=clerk_user_id)
        except Exception as e:
            print(e)
            return None


def get_context() -> Context:
    return Context()
