

def test_conversation_can_be_deleted_by_brand_member(client: TestClient) -> None:
    signup(client, "delete-conversation@example.com")
    brand_id = create_brand(client)
    conversation = client.post(
        f"/api/brands/{brand_id}/conversations",
        json={"title": "Temporary chat"},
    )
    conversation_id = conversation.json()["id"]

    deleted = client.delete(f"/api/conversations/{conversation_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/conversations/{conversation_id}").status_code == 404
from fastapi.testclient import TestClient

from conftest import signup
from test_brands_and_state import create_brand


def test_conversation_and_messages_persist_for_brand_member(
    client: TestClient,
) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)

    conversation = client.post(
        f"/api/brands/{brand_id}/conversations",
        json={"title": "Initial discovery"},
    )
    assert conversation.status_code == 201, conversation.text
    conversation_id = conversation.json()["id"]

    user_message = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={
            "role": "user",
            "content": "대학생을 위한 서비스를 만들고 있어요.",
        },
    )
    assert user_message.status_code == 201, user_message.text

    assistant_message = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={
            "role": "assistant",
            "content": "해결하려는 문제를 더 구체화해볼게요.",
            "artifact": {"type": "discovery"},
        },
    )
    assert assistant_message.status_code == 201, assistant_message.text

    messages = client.get(f"/api/conversations/{conversation_id}/messages")
    assert messages.status_code == 200, messages.text
    assert [item["role"] for item in messages.json()] == ["user", "assistant"]
    assert messages.json()[1]["artifact"]["type"] == "discovery"

    conversations = client.get(f"/api/brands/{brand_id}/conversations")
    assert conversations.status_code == 200, conversations.text
    assert conversations.json()[0]["id"] == conversation_id


def test_user_cannot_access_another_users_conversation(client: TestClient) -> None:
    signup(client, "owner@example.com")
    brand_id = create_brand(client)
    conversation = client.post(
        f"/api/brands/{brand_id}/conversations",
        json={"title": "Private conversation"},
    )
    conversation_id = conversation.json()["id"]

    client.post("/api/auth/logout")
    signup(client, "other@example.com")

    assert client.get(f"/api/conversations/{conversation_id}").status_code == 404
    assert client.get(
        f"/api/conversations/{conversation_id}/messages"
    ).status_code == 404
    assert client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "unauthorized"},
    ).status_code == 404
