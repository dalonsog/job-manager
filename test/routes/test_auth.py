from fastapi.testclient import TestClient
from jobmanager.core.config import settings


def test_login_successful(client: TestClient) -> None:
    payload = {
        "username": "admin@email.com",
        "password": "pwd12345"
    }
    response = client.post("/auth/login", data=payload)
    assert response.status_code == 200
    token: dict = response.json()
    assert token.get("token_type") == "bearer"
    assert token["access_token"]


def test_login_failed(client: TestClient) -> None:
    payload = {
        "username": "admin@email.com",
        "password": "12345678"
    }
    response = client.post("/auth/login", data=payload)
    assert response.status_code == 401
