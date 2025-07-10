import enum
from uuid import UUID


class JobStatus(enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class AutoLabelModel(enum.Enum):
    YOLO_WORLD = "YOLOWorld"
