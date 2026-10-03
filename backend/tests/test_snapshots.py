from fastapi.testclient import TestClient

from conftest import signup
from test_brands_and_state import create_brand


def apply_proposal(client: TestClient, brand_id: str, value: str) -> None:
    proposal = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={
            "title": "Update positioning",
            "summary": "Test snapshot change",
            "changes": {"brand.positioning": value},
        },
    )
    assert proposal.status_code == 201, proposal.text
    proposal_id = proposal.json()["id"]
    assert client.post(f"/api/brands/{brand_id}/proposals/{proposal_id}/approve").status_code == 200
    applied = client.post(f"/api/brands/{brand_id}/proposals/{proposal_id}/apply")
    assert applied.status_code == 200, applied.text


def test_snapshot_restore_reverts_state_and_records_history(client: TestClient) -> None:
    signup(client, "snapshot@example.com")
    brand_id = create_brand(client)

    apply_proposal(client, brand_id, "첫 번째 포지셔닝")
    snapshots = client.get(f"/api/brands/{brand_id}/snapshots")
    assert snapshots.status_code == 200, snapshots.text
    assert len(snapshots.json()) == 1

    apply_proposal(client, brand_id, "두 번째 포지셔닝")
    snapshots = client.get(f"/api/brands/{brand_id}/snapshots")
    assert len(snapshots.json()) == 2
    snapshot_id = snapshots.json()[0]["id"]
    restored = client.post(f"/api/brands/{brand_id}/snapshots/{snapshot_id}/restore")
    assert restored.status_code == 200, restored.text

    state = client.get(f"/api/brands/{brand_id}/state")
    assert state.status_code == 200, state.text
    assert state.json()["state"]["brand"]["positioning"] == "첫 번째 포지셔닝"
    assert state.json()["version"] == 4

    history = client.get(f"/api/brands/{brand_id}/history")
    assert history.status_code == 200, history.text
    assert history.json()[0]["action"] == "snapshot_restored"


def test_snapshot_restore_isolated_by_brand(client: TestClient) -> None:
    signup(client, "snapshot-owner@example.com")
    brand_id = create_brand(client)
    apply_proposal(client, brand_id, "private snapshot")
    snapshot_id = client.get(f"/api/brands/{brand_id}/snapshots").json()[0]["id"]

    client.post("/api/auth/logout")
    signup(client, "snapshot-other@example.com")
    response = client.post(f"/api/brands/{brand_id}/snapshots/{snapshot_id}/restore")
    assert response.status_code == 404
