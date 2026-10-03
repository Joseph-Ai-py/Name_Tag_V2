from fastapi.testclient import TestClient

from conftest import signup
from test_brands_and_state import create_brand


def test_lite_meeting_collects_opinions_and_creates_pending_proposal(client: TestClient) -> None:
    signup(client, "manager@example.com")
    brand_id = create_brand(client)

    response = client.post(
        "/api/agent/meetings",
        json={
            "brand_id": brand_id,
            "agenda": "우리 브랜드의 포지셔닝을 개선해줘",
            "mode": "lite",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "completed"
    assert body["participants"] == ["brand_strategist", "customer_researcher", "business_strategist"]
    assert len(body["opinions"]) == 3
    assert body["critic"]["agreements"]
    assert body["decision"]["proposal_id"]

    proposal_id = body["decision"]["proposal_id"]
    state = client.get(f"/api/brands/{brand_id}/state").json()
    assert state["version"] == 1
    proposal = client.get(f"/api/brands/{brand_id}/proposals/{proposal_id}")
    assert proposal.status_code == 200
    assert proposal.json()["status"] == "pending"

    assert client.post(f"/api/brands/{brand_id}/proposals/{proposal_id}/approve").status_code == 200
    assert client.post(f"/api/brands/{brand_id}/proposals/{proposal_id}/apply").status_code == 200
    assert client.get(f"/api/brands/{brand_id}/state").json()["version"] == 2


def test_meeting_isolation_by_brand(client: TestClient) -> None:
    signup(client, "meeting-owner@example.com")
    brand_id = create_brand(client)
    created = client.post(
        "/api/agent/meetings",
        json={"brand_id": brand_id, "agenda": "고객 타겟을 검토해줘"},
    )
    assert created.status_code == 201
    meeting_id = created.json()["id"]

    client.post("/api/auth/logout")
    signup(client, "meeting-other@example.com")
    response = client.get(f"/api/agent/brands/{brand_id}/meetings/{meeting_id}")
    assert response.status_code == 404


def test_full_meeting_records_discussion_round(client: TestClient) -> None:
    signup(client, "full-meeting@example.com")
    brand_id = create_brand(client)
    response = client.post(
        "/api/agent/meetings",
        json={"brand_id": brand_id, "agenda": "시장과 고객을 함께 검토해줘", "mode": "full"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["mode"] == "full"
    assert body["critic"]["discussion_rounds"] == 1
    assert "market_researcher" in body["participants"]
    assert "customer_researcher" in body["participants"]
