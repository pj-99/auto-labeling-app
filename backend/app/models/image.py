from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Image(BaseModel):
    id: UUID
    image_name: str
    image_url: str
    image_type: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    caption: str = ""
    created_by: UUID
