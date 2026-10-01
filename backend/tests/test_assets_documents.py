from fastapi.testclient import TestClient

from app.models.asset import Asset
from app.models.document import Document
from app.models.document_block import DocumentBlock
from conftest import signup
from test_brands_and_state import create_brand


def test_asset_metadata_crud(client: TestClient) -> None:
    signup(client, "asset@example.com")
    brand_id = create_brand(client)

    created = client.post(
        f"/api/brands/{brand_id}/assets",
        json={
            "type": "logo",
            "filename": "logo.png",
            "mime_type": "image/png",
            "storage_path": "brands/test/logo.png",
            "metadata": {"source": "generated"},
        },
    )
    assert created.status_code == 201, created.text
    asset_id = created.json()["id"]

    listed = client.get(f"/api/brands/{brand_id}/assets")
    assert listed.status_code == 200
    assert listed.json()[0]["metadata"]["source"] == "generated"

    deleted = client.delete(f"/api/brands/{brand_id}/assets/{asset_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/brands/{brand_id}/assets").json() == []


def test_document_and_block_crud(client: TestClient) -> None:
    signup(client, "document@example.com")
    brand_id = create_brand(client)

    created = client.post(
        f"/api/brands/{brand_id}/documents",
        json={"title": "Brand Guide"},
    )
    assert created.status_code == 201, created.text
    document_id = created.json()["id"]

    block = client.post(
        f"/api/brands/{brand_id}/documents/{document_id}/blocks",
        json={"type": "heading", "content": {"text": "Brand Story"}, "position": 0},
    )
    assert block.status_code == 201, block.text
    block_id = block.json()["id"]

    updated = client.patch(
        f"/api/brands/{brand_id}/documents/{document_id}/blocks/{block_id}",
        json={"content": {"text": "Updated Brand Story"}},
    )
    assert updated.status_code == 200
    assert updated.json()["content"]["text"] == "Updated Brand Story"

    document = client.get(f"/api/brands/{brand_id}/documents/{document_id}")
    assert document.status_code == 200
    assert document.json()["blocks"][0]["id"] == block_id

    deleted = client.delete(
        f"/api/brands/{brand_id}/documents/{document_id}/blocks/{block_id}"
    )
    assert deleted.status_code == 204