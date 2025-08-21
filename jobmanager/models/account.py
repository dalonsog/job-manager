import uuid
from sqlmodel import SQLModel, Field


class AccountBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=256)
    is_active: bool = True
    is_global: bool = False


class AccountCreate(AccountBase):
    pass


class AccountRegister(SQLModel):
    name: str = Field(max_length=256)


class AccountPublic(AccountBase):
    id: uuid.UUID
    