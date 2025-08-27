import uuid
import json
from fastapi.testclient import TestClient

account_data = {"name": "account3"}


def test_read_accounts_no_auth(client: TestClient) -> None:
    response = client.get("/accounts/")
    assert response.status_code == 401


def test_read_accounts_invalid_jwt(client: TestClient) -> None:
    response = client.get(
        "/accounts/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_read_accounts_admin(client: TestClient, admin_data: dict) -> None:
    response = client.get(
        "/accounts/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_accounts_user(client: TestClient, maintainer_data: dict) -> None:
    response = client.get(
        "/accounts/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 401


def test_read_account_admin(
    client: TestClient,
    admin_data: dict,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.get(
        f"/accounts/{account_id}",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    data: dict = response.json()
    assert data.get("id") == str(account_id)


def test_read_admin_account_no_privileges(
    client: TestClient,
    admin_data: dict,
    maintainer_data: dict
) -> None:
    account_id = admin_data.get("data").account_id
    response = client.get(
        f"/accounts/{account_id}",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 401


def test_read_account_not_found(
    client: TestClient,
    maintainer_data: dict
) -> None:
    account_id = uuid.uuid4()
    response = client.get(
        f"/accounts/{account_id}",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 404


def test_create_account_no_privileges(
    client: TestClient,
    maintainer_data: dict
) -> None:
    response = client.post(
        "/accounts/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"},
        content=json.dumps(account_data)
    )
    assert response.status_code == 401


def test_create_account_already_exists(
    client: TestClient,
    admin_data: dict
) -> None:
    account_data = {"name": "regular"}
    response = client.post(
        "/accounts/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"},
        content=json.dumps(account_data)
    )
    assert response.status_code == 409


def test_create_account_successful(
    client: TestClient,
    admin_data: dict
) -> None:
    response = client.post(
        "/accounts/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"},
        content=json.dumps(account_data)
    )
    assert response.status_code == 201
    response_data: dict = response.json()
    assert response_data.get("name") == account_data.get("name")
    account_data.update(**response_data)


def test_deactivate_account_no_privileges(
    client: TestClient,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.put(
        f"/accounts/{account_id}/deactivate",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 401


def test_deactivate_account_successful(
    client: TestClient,
    admin_data: dict,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.put(
        f"/accounts/{account_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/accounts/{account_id}/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data: dict = response.json()
    assert response_data.get("id") == str(account_id)
    assert response_data.get("is_active") == False


def test_deactivate_account_already_deactivated(
    client: TestClient,
    admin_data: dict,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.put(
        f"/accounts/{account_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 400


def test_activate_account_no_privileges(
    client: TestClient,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.put(
        f"/accounts/{account_id}/activate",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 401


def test_activate_account_successful(
    client: TestClient,
    admin_data: dict,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.put(
        f"/accounts/{account_id}/activate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/accounts/{account_id}/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data: dict = response.json()
    assert response_data.get("id") == str(account_id)
    assert response_data.get("is_active") == True


def test_activate_account_already_activated(
    client: TestClient,
    admin_data: dict,
    maintainer_data: dict
) -> None:
    account_id = maintainer_data.get("data").account_id
    response = client.put(
        f"/accounts/{account_id}/activate",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 400


def test_delete_account_no_privileges(
    client: TestClient,
    maintainer_data: dict
) -> None:
    response = client.delete(
        f"/accounts/{account_data.get("id")}",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 401


def test_delete_account_successful(
    client: TestClient,
    admin_data: dict
) -> None:
    response = client.delete(
        f"/accounts/{account_data.get("id")}",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/accounts/{account_data.get("id")}",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 404
