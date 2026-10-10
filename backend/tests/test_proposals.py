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


def test_proposal_rejects_unsupported_change_paths(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    response = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={
            "title": "Invalid change",
            "summary": "This should be rejected",
            "changes": {"brand.unknown_field": "bad-value"},
        },
    )

    assert response.status_code == 400, response.text
    assert "Unsupported BrandState path" in response.json()["detail"]


def test_pending_proposal_can_be_deleted_but_applied_proposal_cannot(client: TestClient) -> None:
    signup(client, "delete-proposal@example.com")
    brand_id = create_brand(client)
    created = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={"title": "Remove me", "summary": "Pending proposal", "changes": {"brand.tone": "warm"}},
    )
    proposal_id = created.json()["id"]

    deleted = client.delete(f"/api/brands/{brand_id}/proposals/{proposal_id}")
    assert deleted.status_code == 204, deleted.text
    assert client.get(f"/api/brands/{brand_id}/proposals/{proposal_id}").status_code == 404

    retained = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={"title": "Keep me", "summary": "Applied proposal", "changes": {"brand.tone": "clear"}},
    )
    retained_id = retained.json()["id"]
    assert client.post(f"/api/brands/{brand_id}/proposals/{retained_id}/approve").status_code == 200
    assert client.post(f"/api/brands/{brand_id}/proposals/{retained_id}/apply").status_code == 200
    assert client.delete(f"/api/brands/{brand_id}/proposals/{retained_id}").status_code == 409


def test_nested_market_proposal_is_applied_to_brand_state(client: TestClient) -> None:
    signup(client, "market-proposal@example.com")
    brand_id = create_brand(client)

    proposal = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={
            "title": "Market analysis",
            "summary": "Apply research-backed market fields",
            "changes": {
                "market": {
                    "tam": "Global AI consulting market",
                    "trends": ["Productization"],
                }
            },
        },
    )
    assert proposal.status_code == 201, proposal.text
    proposal_id = proposal.json()["id"]
    assert client.post(f"/api/brands/{brand_id}/proposals/{proposal_id}/approve").status_code == 200
    applied = client.post(f"/api/brands/{brand_id}/proposals/{proposal_id}/apply")
    assert applied.status_code == 200, applied.text

    state = client.get(f"/api/brands/{brand_id}/state").json()["state"]
    assert state["market"]["tam"] == "Global AI consulting market"
    assert state["market"]["trends"] == ["Productization"]


def test_agent_proposal_rejects_stale_brand_state_version(client: TestClient) -> None:
    signup(client, "stale-proposal@example.com")
    brand_id = create_brand(client)

    agent_response = client.post(
        "/api/agent/chat",
        json={"brand_id": brand_id, "message": "우리 브랜드의 포지셔닝을 개선해줘"},
    )
    assert agent_response.status_code == 200, agent_response.text
    stale_proposal_id = agent_response.json()["proposal_id"]

    competing = client.post(
        f"/api/brands/{brand_id}/proposals",
        json={
            "title": "Competing change",
            "summary": "Advance the state first",
            "changes": {"customer.target": "대학생 창업팀"},
        },
    )
    assert competing.status_code == 201, competing.text
    competing_id = competing.json()["id"]
    assert client.post(f"/api/brands/{brand_id}/proposals/{competing_id}/approve").status_code == 200
    assert client.post(f"/api/brands/{brand_id}/proposals/{competing_id}/apply").status_code == 200

    assert client.post(f"/api/brands/{brand_id}/proposals/{stale_proposal_id}/approve").status_code == 200
    applied = client.post(f"/api/brands/{brand_id}/proposals/{stale_proposal_id}/apply")
    assert applied.status_code == 409
    assert applied.json()["detail"]["code"] == "BRAND_STATE_VERSION_CONFLICT"
    assert applied.json()["detail"]["expected_version"] == 1
    assert applied.json()["detail"]["actual_version"] == 2
