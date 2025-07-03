from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from .image import Image


class Dataset(BaseModel):
    id: UUID
    name: str
    images: List[Image]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
