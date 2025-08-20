import enum
import uuid
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Enum, Column, Relationship


class Role(str, enum.Enum):
    DEVELOPER = "dev"
    MAINTAINER = "maintainer"
    ADMIN = "admin"


class Status(str, enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"


class AccountBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=256)
    is_active: bool = True


class AccountCreate(AccountBase):
    password: str = Field(min_length=8, max_length=40)


class Account(AccountBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    users: list["User"] = Relationship(
        back_populates="account",
        cascade_delete=True
    )


class AccountPublic(AccountBase):
    id: uuid.UUID


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=256)
    role: Role = Field(sa_column=Column(Enum(Role)))
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    account_id: uuid.UUID = Field(
        foreign_key="account.id",
        nullable=False,
        ondelete="CASCADE"
    )
    account: Account | None = Relationship(back_populates="account")
    
    jobs: list["Job"] = Relationship(
        back_populates="owner",
        cascade_delete=True
    )


class UserPublic(UserBase):
    id: uuid.UUID
    account_id: uuid.UUID


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
