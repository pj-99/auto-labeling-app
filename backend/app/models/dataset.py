from datetime import datetime
from typing import List
from uuid import UUID

from image import Image
from pydantic import BaseModel


class Dataset(BaseModel):
    id: UUID
    name: str
    images: List[Image]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
