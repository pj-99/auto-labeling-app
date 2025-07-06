import uuid

from api.deps import get_storage_bucket
from pydantic import BaseModel


class GenerateSignedUrlRequest(BaseModel):
    content_type: str = "application/octet-stream"


def generate_signed_url(content_type: str = "application/octet-stream") -> dict:
    if len(content_type.split("/")) < 2 or content_type.split("/")[0] != "image":
        raise ValueError("Invalid content type")

    file_type = content_type.split("/")[1]

    filename = str(uuid.uuid4()) + "." + file_type
    # TODO: check if file already exists
    # TODO: check if file size is too large
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
