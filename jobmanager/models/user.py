import enum
import uuid
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Enum, Column


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


class UserCreateInAccount(UserCreate):
    account_id: uuid.UUID


class UserPublic(UserBase):
    id: uuid.UUID
    account_id: uuid.UUID
