import enum
from uuid import UUID


class JobStatus(enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class AutoLabelModel(enum.Enum):
    YOLO_WORLD = "YOLOWorld"


class AutoLabelJob:
    id: UUID
    status: JobStatus
    model: AutoLabelModel
    dataset_id: UUID
    image_id: UUID
