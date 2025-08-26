import pytest
from typing import Generator
from fastapi.testclient import TestClient
from jobmanager.main import app


client = TestClient(app)

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
