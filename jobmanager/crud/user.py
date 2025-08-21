import uuid
from sqlmodel import Session, select
from jobmanager.models.dbmodels import User
from jobmanager.models.user import UserCreate
from jobmanager.core.security import get_password_hash


def create_user(
    session: Session,
    user: UserCreate,
    account_id: uuid.UUID
) -> User:
    user_db = User.model_validate(
        user,
        update={
            "hashed_password": get_password_hash(user.password),
            "account_id": account_id
        }
    )
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db
