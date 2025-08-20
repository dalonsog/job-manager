import enum
import uuid
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Enum, Column, Relationship


if TYPE_CHECKING:
    from jobmanager.models.user import User


class Status(str, enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"


class JobBase(SQLModel):
    name: str
    command: str


class JobCreate(JobBase):
    pass


class Job(JobBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: Status = Field(sa_column=Column(Enum(Status)))
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User = Relationship(back_populates="jobs")


class JobPublic(JobBase):
    id: uuid.UUID
    status: Status
    owner_id: uuid.UUID
