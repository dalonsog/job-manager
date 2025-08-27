from sqlmodel import SQLModel, Session
from jobmanager.crud.account import create_account
from jobmanager.crud.user import create_user
from jobmanager.crud.job import create_job
from jobmanager.models.dbmodels import Account, User, Job
from jobmanager.models.account import AccountCreate
from jobmanager.models.user import UserCreate, Role
from jobmanager.models.job import JobCreate, Status
from jobmanager.core.config import settings


def init_test_db(engine):
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        accounts = _create_accounts(session)
        users = _create_users(session, accounts)
        _ = _create_jobs(session, users)


def _create_accounts(session) -> dict[str, Account]:
    return {
        "admin": create_account(
            session=session,
            account=AccountCreate(name="admin", is_global=True)
        ),
        "regular": create_account(
            session=session,
            account=AccountCreate(name="regular", is_global=False)
        )
    }


def _create_users(
    session: Session,
    accounts: dict[str, Account]
) -> dict[str, User]:
    return {
        "admin": create_user(
            session=session, 
            user=UserCreate(
                email="admin@email.com",
                password="pwd12345",
                role=Role.ADMIN,
            ), 
            account_id=accounts.get("admin").id
        ),
        "maintainer": create_user(
            session=session, 
            user=UserCreate(
                email="maintainer@email.com",
                password="pwd12345",
                role=Role.MAINTAINER,
            ), 
            account_id=accounts.get("regular").id
        ),
        "developer1": create_user(
            session=session, 
            user=UserCreate(
                email="dev1@email.com",
                password="pwd12345",
                role=Role.DEVELOPER,
            ), 
            account_id=accounts.get("regular").id
        ),
        "developer2": create_user(
            session=session, 
            user=UserCreate(
                email="dev2@email.com",
                password="pwd12345",
                role=Role.DEVELOPER,
            ), 
            account_id=accounts.get("regular").id
        )
    }


def _create_jobs(session: Session, users: dict[str, User]) -> dict[str, Job]:
    return {
        "job1": create_job(
            session=session,
            job=JobCreate(
                name="job1",
                command="cd.. && npm ci"
            ),
            owner_id=users.get("developer1").id,
            status=Status.RUNNING
        ),
        "job2": create_job(
            session=session,
            job=JobCreate(
                name="job2",
                command="cd.. && npm ci"
            ),
            owner_id=users.get("developer1").id,
            status=Status.RUNNING
        ),
        "job3": create_job(
            session=session,
            job=JobCreate(
                name="job3",
                command="cd.. && npm ci"
            ),
            owner_id=users.get("developer1").id,
            status=Status.STOPPED
        ),
        "job4": create_job(
            session=session,
            job=JobCreate(
                name="job4",
                command="cd.. && npm ci"
            ),
            owner_id=users.get("developer1").id,
            status=Status.RUNNING
        ),
        "job5": create_job(
            session=session,
            job=JobCreate(
                name="job5",
                command="cd.. && npm ci"
            ),
            owner_id=users.get("developer2").id,
            status=Status.RUNNING
        ),
        "job6": create_job(
            session=session,
            job=JobCreate(
                name="job6",
                command="cd.. && npm ci"
            ),
            owner_id=users.get("developer2").id,
            status=Status.STOPPED
        ),
    }
