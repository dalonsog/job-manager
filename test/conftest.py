import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from jobmanager.main import app
from jobmanager.core.deps import SessionDep, get_session
#from jobmanager.core.db import engine
from test.utils.db import init_test_db


TEST_DATABASE_URL = "sqlite:///test_database.db"


@pytest.fixture(scope="session", autouse=True)
def session():
    connect_args = {"check_same_thread": False}
    _engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
    try:
        SQLModel.metadata.drop_all(_engine)
    except:
        pass
    init_test_db(_engine)
    with Session(_engine) as session:
        yield session
    SQLModel.metadata.drop_all(_engine)



@pytest.fixture(scope="module")
def client(session) -> Generator[TestClient, None, None]:
    def override_get_session():
        return session
    
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_jwt(client: TestClient) -> str:
    login_data = {
        "username": "admin@email.com",
        "password": "pwd12345",
    }
    r = client.post(f"/auth/login/", data=login_data)
    token: dict = r.json()
    return token.get("access_token")


