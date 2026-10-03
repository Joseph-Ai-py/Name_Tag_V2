from fastapi.testclient import TestClient

from conftest import signup


def create_brand(client: TestClient) -> str:
    response = client.post(
        "/api/brands",
        json={"name": "Test Brand", "description": "Initial"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_brand_crud_and_state_patch_preserves_other_sections(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    detail = client.get(f"/api/brands/{brand_id}")
    assert detail.status_code == 200, detail.text
    assert detail.json()["name"] == "Test Brand"

    update = client.patch(
        f"/api/brands/{brand_id}",
        json={"name": "Updated Brand"},
    )
    assert update.status_code == 200, update.text
    assert update.json()["name"] == "Updated Brand"
    assert update.json()["description"] == "Initial"

    initial_state = client.get(f"/api/brands/{brand_id}/state")
    assert initial_state.status_code == 200, initial_state.text
    initial_version = initial_state.json()["version"]

    state_update = client.patch(
        f"/api/brands/{brand_id}/state",
        json={
            "state": {"business": {"service": "AI Workspace"}},
            "expected_version": initial_version,
        },
    )
    assert state_update.status_code == 200, state_update.text
    body = state_update.json()
    assert body["version"] == initial_version + 1
    assert body["state"]["business"]["service"] == "AI Workspace"
    assert body["state"]["customer"]["target"] is None
    assert body["state"]["visual"]["colors"] == []

    stale_update = client.patch(
        f"/api/brands/{brand_id}/state",
        json={
            "state": {"brand": {"tone": "warm"}},
            "expected_version": initial_version,
        },
    )
    assert stale_update.status_code == 409, stale_update.text


def test_user_cannot_access_or_delete_another_users_brand(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    client.post("/api/auth/logout")
    signup(client, "other@example.com")

    assert client.get(f"/api/brands/{brand_id}").status_code == 404
    assert client.get(f"/api/brands/{brand_id}/state").status_code == 404
    assert client.patch(
        f"/api/brands/{brand_id}",
        json={"name": "Hijacked"},
    ).status_code == 404
    assert client.delete(f"/api/brands/{brand_id}").status_code == 404


def test_brand_state_patch_rejects_unsupported_fields(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    response = client.patch(
        f"/api/brands/{brand_id}/state",
        json={
            "state": {"brand": {"not_a_real_field": "bad-value"}},
            "expected_version": 1,
        },
    )

    assert response.status_code == 400, response.text
    assert "Unsupported BrandState path" in response.json()["detail"]


def test_owner_can_delete_brand(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    deleted = client.delete(f"/api/brands/{brand_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/brands/{brand_id}").status_code == 404
