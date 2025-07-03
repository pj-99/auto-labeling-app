import uuid

from api.deps import get_storage_bucket
from pydantic import BaseModel


class GenerateSignedUrlRequest(BaseModel):
    content_type: str = "application/octet-stream"


def generate_signed_url(content_type: str = "application/octet-stream") -> dict:
    filename = f"{uuid.uuid4()}.jpg"
    blob = get_storage_bucket().blob(filename)

    url = blob.generate_signed_url(
        version="v4",
        expiration=600,
        method="PUT",
        content_type=content_type,
    )
    return {
        "filename": filename,
        "url": url,
    }
