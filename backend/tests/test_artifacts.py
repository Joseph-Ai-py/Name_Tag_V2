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


def test_customer_artifact_apply_maps_ai_field_names(client: TestClient) -> None:
    signup(client, "customer-artifact@example.com")
    brand_id = create_brand(client)
    created = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={
            "type": "customer_analysis",
            "title": "Customer analysis",
            "content": {
                "customer": {
                    "target_segment": "초기 AI 스타트업",
                    "persona": {"name": "AI 스타트업 CTO"},
                    "jtbd": "모델을 시장에 출시하기",
                },
            },
        },
    )
    assert created.status_code == 201, created.text
    artifact_id = created.json()["id"]

    applied = client.post(f"/api/brands/{brand_id}/artifacts/{artifact_id}/apply")
    assert applied.status_code == 200, applied.text
    state = client.get(f"/api/brands/{brand_id}/state")
    assert state.json()["state"]["customer"]["target"] == "초기 AI 스타트업"
    assert state.json()["state"]["customer"]["persona"] == {"name": "AI 스타트업 CTO"}
    assert state.json()["state"]["customer"]["jtbd"] == "모델을 시장에 출시하기"


def test_brand_identity_artifact_apply_maps_nested_fields(client: TestClient) -> None:
    signup(client, "brand-artifact@example.com")
    brand_id = create_brand(client)
    created = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={
            "type": "brand_identity",
            "title": "Brand identity update",
            "content": {
                "brand identity update": {
                    "core_value": "추진력",
                    "value_proposition": "완결형 빌더",
                    "brand_essence": "현장의 성과로 바꾸는 해결사",
                    "target_slogan": "비즈니스 완결성 100%",
                },
            },
        },
    )
    assert created.status_code == 201, created.text
    applied = client.post(f"/api/brands/{brand_id}/artifacts/{created.json()['id']}/apply")
    assert applied.status_code == 200, applied.text
    state = client.get(f"/api/brands/{brand_id}/state").json()["state"]
    assert state["brand"]["values"] == "추진력"
    assert state["brand"]["key_message"] == "완결형 빌더"
    assert state["brand"]["positioning"] == "현장의 성과로 바꾸는 해결사"
    assert state["brand"]["tagline"] == "비즈니스 완결성 100%"


def test_brand_strategy_wrapper_artifact_apply_maps_brand_fields(client: TestClient) -> None:
    signup(client, "brand-wrapper@example.com")
    brand_id = create_brand(client)
    created = client.post(
        f"/api/brands/{brand_id}/artifacts",
        json={
            "type": "brand_strategy",
            "title": "Brand identity update",
            "content": {"brand identity update": {"brand_essence": "현장의 성과로 바꾸는 해결사"}},
        },
    )
    applied = client.post(f"/api/brands/{brand_id}/artifacts/{created.json()['id']}/apply")
    assert applied.status_code == 200, applied.text
    assert client.get(f"/api/brands/{brand_id}/state").json()["state"]["brand"]["positioning"] == "현장의 성과로 바꾸는 해결사"
