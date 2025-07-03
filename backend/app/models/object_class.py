from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Class(BaseModel):
    id: int
    name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
