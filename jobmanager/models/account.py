import uuid
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from jobmanager.models.user import User


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
    