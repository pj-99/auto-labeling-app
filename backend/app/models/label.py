from pydantic import BaseModel


class LabelBase(BaseModel):
    class_id: int
