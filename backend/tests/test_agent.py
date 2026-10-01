from fastapi.testclient import TestClient

from conftest import signup
from test_brands_and_state import create_brand


def test_agent_chat_routes_and_persists_artifact_and_messages(
    client: TestClient,
) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    response = client.post(
        "/api/agent/chat",
        json={
            "brand_id": brand_id,
            "message": "우리 타겟 고객을 정리해줘",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["route"] == "customer"
    assert body["conversation_id"]
    assert body["artifact"]["status"] == "draft"
    assert body["artifact"]["type"] == "customer_analysis"

    conversation_id = body["conversation_id"]
    messages = client.get(f"/api/conversations/{conversation_id}/messages")
    assert messages.status_code == 200, messages.text
    assert [item["role"] for item in messages.json()] == ["user", "assistant"]

    follow_up = client.post(
        "/api/agent/chat",
        json={
            "brand_id": brand_id,
            "conversation_id": conversation_id,
            "message": "고마워",
        },
    )
    assert follow_up.status_code == 200, follow_up.text
    assert follow_up.json()["route"] == "conversation"
    assert follow_up.json()["artifact"] is None


def test_agent_rejects_unknown_conversation_and_other_user(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    missing = client.post(
        "/api/agent/chat",
        json={
            "brand_id": brand_id,
            "conversation_id": "missing",
            "message": "hello",
        },
    )
    assert missing.status_code == 404

    client.post("/api/auth/logout")
    signup(client, "other@example.com")
    forbidden = client.post(
        "/api/agent/chat",
        json={"brand_id": brand_id, "message": "hello"},
    )
    assert forbidden.status_code == 404
