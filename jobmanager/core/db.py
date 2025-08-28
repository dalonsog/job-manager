from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import Engine
from jobmanager.models.dbmodels import User, Account
from jobmanager.models.account import AccountCreate
from jobmanager.models.user import UserCreate, Role
from jobmanager.core.config import settings
from jobmanager.crud.account import create_account
from jobmanager.crud.user import create_user


def get_engine():
    database_url = (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )
    return create_engine(database_url, echo=False)


def init_db(engine: Engine):
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # create admin account if it does not exist
        statement = select(Account).where(
            Account.name == settings.ADMIN_ACCOUNT
        )
        admin_account = session.exec(statement).first()
        if not admin_account:
            account_in = AccountCreate(
                name=settings.ADMIN_ACCOUNT,
                is_global=True,
            )
            admin_account = create_account(session=session, account=account_in)
            print(f'Created admin account {admin_account.name}')

        # create admin user if it does not exist
        statement = select(User).where(
            User.email == settings.ADMIN_EMAIL
        )
        admin_user = session.exec(statement).first()
        if not admin_user:
            user_in = UserCreate(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                role=Role.ADMIN,
            )
            admin_user = create_user(
                session=session, 
                user=user_in, 
                account_id=admin_account.id
            )
            print(f'Created admin user {admin_user.email}')
