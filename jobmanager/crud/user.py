import uuid
from sqlmodel import Session, select
from jobmanager.models.dbmodels import User
from jobmanager.models.user import UserCreate
from jobmanager.core.security import get_password_hash, verify_password


def get_user_by_email(session: Session, user_email: str) -> User:
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()
    return user


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


def authenticate_user(
    session: Session,
    user_email: str,
    user_pwd: str
) -> User | bool:
    user = get_user_by_email(session, user_email)
    if not user or not verify_password(user_pwd, user.hashed_password):
        return False
    return user