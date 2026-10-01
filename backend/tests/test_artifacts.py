from fastapi.testclient import TestClient

from conftest import signup
from test_brands_and_state import create_brand


def test_artifact_lifecycle(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    created = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={
            "type": "brand_strategy",
            "title": "Positioning proposal",
            "content": {"positioning": "A focused workspace"},
        },
    )
    assert created.status_code == 201, created.text
    artifact_id = created.json()["id"]
    assert created.json()["status"] == "draft"

    listed = client.get(f"/api/brands/{brand_id}/artifacts")
    assert listed.status_code == 200, listed.text
    assert listed.json()[0]["id"] == artifact_id

    approved = client.post(
        f"/api/brands/{brand_id}/artifacts/{artifact_id}/approve",
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"

    second_approval = client.post(
        f"/api/brands/{brand_id}/artifacts/{artifact_id}/approve",
    )
    assert second_approval.status_code == 409, second_approval.text


def test_user_cannot_access_another_users_artifact(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)
    created = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={"type": "draft", "title": "Private", "content": {}},
    )
    artifact_id = created.json()["id"]

    client.post("/api/auth/logout")
    signup(client, "other@example.com")

    assert client.get(f"/api/brands/{brand_id}/artifacts").status_code == 404
    assert client.get(
        f"/api/brands/{brand_id}/artifacts/{artifact_id}"
    ).status_code == 404


def test_artifact_apply_updates_brand_state(client: TestClient) -> None:
    signup(client, "apply-artifact@example.com")
    brand_id = create_brand(client)
    created = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={
            "type": "brand_strategy",
            "title": "Selected direction",
            "content": {"positioning": "문제를 해결하는 AI Product Builder"},
        },
    )
    artifact_id = created.json()["id"]

    applied = client.post(f"/api/brands/{brand_id}/artifacts/{artifact_id}/apply")
    assert applied.status_code == 200, applied.text
    assert applied.json()["status"] == "applied"

    state = client.get(f"/api/brands/{brand_id}/state")
    assert state.json()["state"]["brand"]["positioning"] == "문제를 해결하는 AI Product Builder"
