from uuid import UUID

import jwt
from api.deps import settings


def get_current_user_from_token(token: str) -> tuple[UUID, str]:
    payload = jwt.decode(
        token,
        settings.CLERK_JWT_KEY,
        algorithms=["RS256"],
    )
    user_id = UUID(payload.get("user_external_id"))
    clerk_user_id = payload.get("user_id")
    return user_id, clerk_user_id
