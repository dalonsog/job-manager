import uuid
from sqlmodel import Session, select
from jobmanager.models.dbmodels import User
from jobmanager.models.user import UserCreate
from jobmanager.core.security import get_password_hash, verify_password


def get_user_by_email(session: Session, user_email: str) -> User:
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()
    return user


def get_user_by_id(session: Session, user_id: uuid.UUID) -> User:
    user = session.get(User, user_id)
    return user


def get_users(
    session: Session,
    offset: int,
    limit: int,
    account_id: uuid.UUID | None = None
) -> list[User]:
    if account_id:
        pre_statement = select(User).where(User.account_id == account_id)
    else:
        pre_statement = select(User)
    statement = pre_statement.offset(offset).limit(limit)
    users = session.exec(statement).all()
    return users


def get_all_users(
    session: Session,
    account_id: uuid.UUID | None = None
) -> list[User]:
    if account_id:
        statement = select(User).where(User.account_id == account_id)
    else:
        statement = select(User)
    users = session.exec(statement).all()
    return users


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


def remove_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()


def update_user(session: Session, user: User, user_in: User) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    user.sqlmodel_update(user_data, update=extra_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
