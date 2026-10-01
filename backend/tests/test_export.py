from fastapi.testclient import TestClient

from app.models.asset import Asset
from conftest import signup
from test_brands_and_state import create_brand


def test_json_export_contains_workspace_data(client: TestClient) -> None:
    signup(client, "export@example.com")
    brand_id = create_brand(client)

    client.patch(
        f"/api/brands/{brand_id}/state",
        json={"state": {"brand": {"name": "Export Brand"}}},
    )
    artifact = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={"type": "brand_strategy", "title": "Strategy", "content": {"mission": "Build"}},
    )
    assert artifact.status_code == 201
    asset = client.post(
        f"/api/brands/{brand_id}/assets",
        json={
            "type": "logo",
            "filename": "logo.png",
            "mime_type": "image/png",
            "storage_path": "brands/export/logo.png",
        },
    )
    assert asset.status_code == 201

    response = client.post(f"/api/brands/{brand_id}/export", json={"format": "json"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["format"] == "json"
    assert body["brand_state"]["state"]["brand"]["name"] == "Export Brand"
    assert body["artifacts"][0]["title"] == "Strategy"
    assert body["assets"][0]["filename"] == "logo.png"