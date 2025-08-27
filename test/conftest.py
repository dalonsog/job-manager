import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
from jobmanager.main import app
from jobmanager.core.deps import get_session
from jobmanager.crud.user import authenticate_user
from jobmanager.core.security import create_access_token
from test.utils.db import init_test_db
from test.utils.user import get_user_data


TEST_DATABASE_URL = "sqlite:///test_database.db"


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    connect_args = {"check_same_thread": False}
    _engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
    try:
        SQLModel.metadata.drop_all(_engine)
    except:
        pass
    init_test_db(_engine)
    yield _engine
    SQLModel.metadata.drop_all(_engine)


@pytest.fixture(scope="module", autouse=True)
def session(engine) -> Generator[Session, None, None]:
    with Session(engine) as _session:
        yield _session


@pytest.fixture(scope="module")
def client(session) -> Generator[TestClient, None, None]:
    def override_get_session():
        return session
    
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_data(session: Session) -> str:
    return get_user_data(
        session=session,
        email="admin@email.com",
        password="pwd12345"
    )


@pytest.fixture(scope="module")
def maintainer_data(session: Session) -> str:
    return get_user_data(
        session=session,
        email="maintainer@email.com",
        password="pwd12345"
    )


@pytest.fixture(scope="module")
def dev1_data(session: Session) -> str:
    return get_user_data(
        session=session,
        email="dev1@email.com",
        password="pwd12345"
    )


@pytest.fixture(scope="module")
def dev2_data(session: Session) -> str:
    return get_user_data(
        session=session,
        email="dev2@email.com",
        password="pwd12345"
    )
