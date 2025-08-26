from fastapi.testclient import TestClient
from jobmanager.core.config import VERSION


def test_health_check(client: TestClient) -> None:
    response = client.get("/system/health-check")
    assert response.status_code == 200
    assert response.json() == True


def test_version(client: TestClient) -> None:
    response = client.get("/system/version")
    assert response.status_code == 200
    assert response.json() == {"message": VERSION}
