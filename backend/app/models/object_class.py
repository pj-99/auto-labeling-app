from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Class(BaseModel):
    id: int
    name: str
    dataset_id: UUID
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
