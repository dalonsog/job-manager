from fastapi.testclient import TestClient


def test_get_users_no_auth(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 401


def test_get_users_invalid_jwt(client: TestClient):
    response = client.get(
        "/users/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_get_users_admin(client: TestClient, admin_jwt: str):
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_jwt}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
