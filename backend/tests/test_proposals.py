from fastapi.testclient import TestClient

from conftest import signup
from test_brands_and_state import create_brand


def test_proposal_requires_approval_and_creates_history(
    client: TestClient,
) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    proposal = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={
            "title": "Refine target",
            "summary": "Make the target more specific",
            "changes": {"customer.target": "대학생 창업팀"},
        },
    )
    assert proposal.status_code == 201, proposal.text
    proposal_id = proposal.json()["id"]

    before_approval = client.post(
        f"/api/brands/{brand_id}/proposals/{proposal_id}/apply",
    )
    assert before_approval.status_code == 409, before_approval.text

    approved = client.post(
        f"/api/brands/{brand_id}/proposals/{proposal_id}/approve",
    )
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "approved"

    applied = client.post(
        f"/api/brands/{brand_id}/proposals/{proposal_id}/apply",
    )
    assert applied.status_code == 200, applied.text
    assert applied.json()["status"] == "applied"

    state = client.get(f"/api/brands/{brand_id}/state")
    assert state.status_code == 200, state.text
    assert state.json()["state"]["customer"]["target"] == "대학생 창업팀"
    assert state.json()["version"] == 2

    history = client.get(f"/api/brands/{brand_id}/history")
    assert history.status_code == 200, history.text
    assert history.json()[0]["action"] == "proposal_applied"
