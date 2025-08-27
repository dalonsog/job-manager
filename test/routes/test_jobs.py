import uuid
import json
from fastapi.testclient import TestClient
from jobmanager.models.dbmodels import User
from jobmanager.models.job import Status


job_data = {"name": "job7", "command": "cd.. && npm ci"}


def test_read_jobs_in_account(client: TestClient, dev1_data: dict) -> None:
    response = client.get(
        "/jobs/",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 6


def test_read_jobs_running_in_account(
    client: TestClient,
    dev1_data: dict
) -> None:
    response = client.get(
        "/jobs/?status=running",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 4


def test_read_jobs_stopped_in_account(
    client: TestClient,
    dev1_data: dict
) -> None:
    response = client.get(
        "/jobs/?status=stopped",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2


def test_read_jobs_owned(client: TestClient, dev1_data: dict) -> None:
    response = client.get(
        "/jobs/own/",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 4


def test_read_jobs_owned_running(client: TestClient, dev1_data: dict) -> None:
    response = client.get(
        "/jobs/own/?status=running",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 3


def test_read_jobs_owned_stopped(client: TestClient, dev1_data: dict) -> None:
    response = client.get(
        "/jobs/own/?status=stopped",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1


def test_read_jobs_all_no_privileges(
    client: TestClient,
    dev1_data: dict
) -> None:
    response = client.get(
        "/jobs/all/",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 401


def test_read_jobs_all_successful(
    client: TestClient,
    admin_data: dict
) -> None:
    response = client.get(
        "/jobs/all/",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 6


def test_read_jobs_all_running(
    client: TestClient,
    admin_data: dict
) -> None:
    response = client.get(
        "/jobs/all/?status=running",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 4


def test_read_jobs_all_stopped(
    client: TestClient,
    admin_data: dict
) -> None:
    response = client.get(
        "/jobs/all/?status=stopped",
        headers={"Authorization": f"Bearer {admin_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2


def test_read_job(client: TestClient, dev1_data: dict) -> None:
    user: User = dev1_data.get("data")
    job = user.jobs[0]
    
    response = client.get(
        f"/jobs/{job.id}",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200
    response_data: dict = response.json()
    assert response_data.get("id") == str(job.id)
    assert response_data.get("name") == job.name
    assert response_data.get("command") == job.command


def test_read_job_not_found(client: TestClient, dev1_data: dict) -> None:
    response = client.get(
        f"/jobs/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 404


def test_create_job(client: TestClient, dev1_data: dict) -> None:
    response = client.post(
        "/jobs/",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"},
        content=json.dumps(job_data)
    )
    assert response.status_code == 201
    response_data: dict = response.json()
    assert response_data.get("name") == job_data.get("name")
    assert response_data.get("command") == job_data.get("command")
    assert response_data.get("status") == Status.STOPPED
    job_data.update(**response_data)


def test_run_job_successful(client: TestClient, dev1_data: dict) -> None:
    response = client.put(
        f"/jobs/{job_data.get("id")}/run",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200


def test_run_job_already_running(client: TestClient, dev1_data: dict) -> None:
    response = client.put(
        f"/jobs/{job_data.get("id")}/run",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 400


def test_run_job_not_owned(client: TestClient, dev2_data: dict) -> None:
    response = client.put(
        f"/jobs/{job_data.get("id")}/run",
        headers={"Authorization": f"Bearer {dev2_data.get("token")}"}
    )
    assert response.status_code == 401


def test_stop_job_successful(client: TestClient, dev1_data: dict) -> None:
    response = client.put(
        f"/jobs/{job_data.get("id")}/stop",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 200


def test_stop_job_already_stopped(client: TestClient, dev1_data: dict) -> None:
    response = client.put(
        f"/jobs/{job_data.get("id")}/stop",
        headers={"Authorization": f"Bearer {dev1_data.get("token")}"}
    )
    assert response.status_code == 400


def test_stop_job_not_owned(client: TestClient, dev2_data: dict) -> None:
    response = client.put(
        f"/jobs/{job_data.get("id")}/stop",
        headers={"Authorization": f"Bearer {dev2_data.get("token")}"}
    )
    assert response.status_code == 401


def test_delete_job_not_owned(client: TestClient, dev2_data: dict) -> None:
    response = client.delete(
        f"/jobs/{job_data.get("id")}/",
        headers={"Authorization": f"Bearer {dev2_data.get("token")}"}
    )
    assert response.status_code == 401


def test_delete_job_by_maintainer(
    client: TestClient,
    maintainer_data: dict
) -> None:
    response = client.delete(
        f"/jobs/{job_data.get("id")}/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 200
    response = client.get(
        f"/jobs/{job_data.get("id")}/",
        headers={"Authorization": f"Bearer {maintainer_data.get("token")}"}
    )
    assert response.status_code == 404
