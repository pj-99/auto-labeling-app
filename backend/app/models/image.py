from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Image(BaseModel):
    id: UUID
    file_name: str
    image_url: str
    created_at: datetime
    updated_at: datetime
    caption: str
    created_by: UUID
