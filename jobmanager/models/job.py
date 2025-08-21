import enum
import uuid
from sqlmodel import SQLModel


class Status(str, enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"


class JobBase(SQLModel):
    name: str
    command: str


class JobCreate(JobBase):
    pass


class JobPublic(JobBase):
    id: uuid.UUID
    status: Status
    owner_id: uuid.UUID
