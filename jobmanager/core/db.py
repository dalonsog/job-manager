import os
from sqlmodel import SQLModel, Session, create_engine, select
from jobmanager.models.dbmodels import User, Account
from jobmanager.models.account import AccountCreate
from jobmanager.models.user import UserCreate, Role
from jobmanager.crud.account import create_account
from jobmanager.crud.user import create_user


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def init_db():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # create admin account if it does not exist
        statement = select(Account).where(
            Account.name == os.environ.get('ADMIN_ACCOUNT')
        )
        admin_account = session.exec(statement).first()
        if not admin_account:
            account_in = AccountCreate(
                name=os.environ.get('ADMIN_ACCOUNT'),
                is_global=True,
            )
            admin_account = create_account(session=session, account=account_in)
            print(f'Created admin account {admin_account.name}')

        # create admin user if it does not exist
        statement = select(User).where(
            User.email == os.environ.get('ADMIN_EMAIL')
        )
        admin_user = session.exec(statement).first()
        if not admin_user:
            user_in = UserCreate(
                email=os.environ.get('ADMIN_EMAIL'),
                password=os.environ.get('ADMIN_PASSWORD'),
                role=Role.ADMIN,
            )
            admin_user = create_user(
                session=session, 
                user=user_in, 
                account_id=admin_account.id
            )
            print(f'Created admin user {admin_user.email}')
