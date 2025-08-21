import uuid
from sqlmodel import Field, Enum, Column, Relationship
from jobmanager.models.account import AccountBase
from jobmanager.models.user import UserBase
from jobmanager.models.job import JobBase, Status


class Account(AccountBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    users: list["User"] = Relationship(
        back_populates="account",
        cascade_delete=True
    )


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    account_id: uuid.UUID = Field(
        foreign_key="account.id",
        nullable=True,
        ondelete="CASCADE"
    )
    account: Account = Relationship(back_populates="users")
    
    jobs: list["Job"] = Relationship(
        back_populates="owner",
        cascade_delete=True
    )


class Job(JobBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: Status = Field(sa_column=Column(Enum(Status)))
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User = Relationship(back_populates="jobs")
