import enum
import uuid
from typing import TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Enum, Column, Relationship


if TYPE_CHECKING:
    from jobmanager.models.job import Job
    from jobmanager.models.account import Account


class Role(str, enum.Enum):
    DEVELOPER = "dev"
    MAINTAINER = "maintainer"
    ADMIN = "admin"


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
