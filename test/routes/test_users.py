import uuid
import json
from fastapi.testclient import TestClient
from jobmanager.models.user import Role


def test_read_users_no_auth(client: TestClient) -> None:
    response = client.get("/users/")
    assert response.status_code == 401


def test_read_users_invalid_jwt(client: TestClient) -> None:
    response = client.get(
        "/users/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_read_users_admin(client: TestClient, admin_data: dict) -> None:
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


def test_read_users_dev(client: TestClient, dev1_data: dict) -> None:
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_read_user_successful(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    user_id = dev1_data.get("data").id
    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    data: dict = response.json()
    assert data.get("id") == str(user_id)


def test_read_user_no_privileges(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    admin_id = admin_data.get("data").id
    response = client.get(
        f"/users/{admin_id}",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 404


def test_read_user_not_found(
    client: TestClient,
    admin_data: dict
) -> None:
    user_id = str(uuid.uuid4())
    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 404


def test_create_user_already_exists(
    client: TestClient,
    maintainer_data: dict,
    dev1_data: dict
) -> None:
    new_user_data = {
        "email": dev1_data.get("data").email,
        "password": "pwd12345",
        "role": Role.DEVELOPER
    }
    response = client.post(
        f"/users/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"},
        content=json.dumps(new_user_data)
    )
    assert response.status_code == 409


def test_create_user_successful(
    client: TestClient,
    maintainer_data: dict
) -> None:
    new_user_data = {
        "email": "dev3@email.com",
        "password": "pwd12345",
        "role": Role.DEVELOPER
    }
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"},
        content=json.dumps(new_user_data)
    )
    assert response.status_code == 201
    response_data: dict = response.json()
    assert response_data.get("email") == new_user_data.get("email")
    assert response_data.get("role") == new_user_data.get("role")
    assert response_data.get("account_id") == str(
        maintainer_data.get("data").account_id)


def test_create_admin_no_privileges(
    client: TestClient,
    maintainer_data: dict
) -> None:
    new_admin_data = {
        "email": "admin2@email.com",
        "password": "pwd12345",
        "role": Role.ADMIN
    }
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"},
        content=json.dumps(new_admin_data)
    )
    assert response.status_code == 401


def test_create_admin_successful(
    client: TestClient,
    admin_data: dict
) -> None:
    new_admin_data = {
        "email": "admin2@email.com",
        "password": "pwd12345",
        "role": Role.ADMIN
    }
    response = client.post(
        f"/users/?account_id={admin_data.get("data").account_id}",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"},
        content=json.dumps(new_admin_data)
    )
    assert response.status_code == 201
    response_data: dict = response.json()
    assert response_data.get("email") == new_admin_data.get("email")
    assert response_data.get("role") == new_admin_data.get("role")
    assert response_data.get("account_id") == str(
        admin_data.get("data").account_id)


def test_deactivate_user_successful(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    user_id = dev1_data.get("data").id
    response = client.put(
        f"/users/{user_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/users/{user_id}/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data: dict = response.json()
    assert response_data.get("is_active") == False


def test_deactivate_user_already_deactivated(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    user_id = dev1_data.get("data").id
    response = client.put(
        f"/users/{user_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 400


def test_activate_user_successful(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    user_id = dev1_data.get("data").id
    response = client.put(
        f"/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/users/{user_id}/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data: dict = response.json()
    assert response_data.get("is_active") == True


def test_activate_user_already_deactivated(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    user_id = dev1_data.get("data").id
    response = client.put(
        f"/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 400


def test_delete_user_successful(
    client: TestClient,
    admin_data: dict,
    dev1_data: dict
) -> None:
    user_id = dev1_data.get("data").id
    response = client.delete(
        f"/users/{user_id}/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/users/{user_id}/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 404
