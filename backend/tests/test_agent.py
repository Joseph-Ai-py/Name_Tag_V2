from fastapi.testclient import TestClient

from app.models.agent_run import AgentRun
from app.models.tool_call import ToolCall
from app.llm.schemas import LLMResponse
from app.services import agent_service
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


def test_agent_brand_request_creates_pending_proposal_without_mutation(client: TestClient) -> None:
    signup(client, "agent-brand@example.com")
    brand_id = create_brand(client)

    response = client.post(
        "/api/agent/chat",
        json={"brand_id": brand_id, "message": "우리 브랜드의 포지셔닝을 개선해줘"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["route"] == "brand"
    assert body["proposal_id"]
    assert body["context"]["tool_results"]["get_brand_state"]["version"] == 1
    assert body["context"]["tool_results"]["get_brand_context"]

    state_before = client.get(f"/api/brands/{brand_id}/state").json()
    assert state_before["state"]["brand"]["positioning"] is None

    proposal = client.get(f"/api/brands/{brand_id}/proposals/{body['proposal_id']}")
    assert proposal.status_code == 200
    assert proposal.json()["status"] == "pending"

    approved = client.post(f"/api/brands/{brand_id}/proposals/{body['proposal_id']}/approve")
    assert approved.status_code == 200
    applied = client.post(f"/api/brands/{brand_id}/proposals/{body['proposal_id']}/apply")
    assert applied.status_code == 200
    state_after = client.get(f"/api/brands/{brand_id}/state").json()
    assert state_after["state"]["brand"]["positioning"]
    assert state_after["version"] == 2

    from app.dependencies import get_database

    db_generator = client.app.dependency_overrides[get_database]()
    db = next(db_generator)
    try:
        run = db.query(AgentRun).filter(AgentRun.id.is_not(None)).order_by(AgentRun.created_at.desc()).first()
        assert run is not None
        assert run.status == "completed"
        calls = db.query(ToolCall).filter(ToolCall.agent_run_id == run.id).all()
        assert [call.tool_name for call in calls] == ["get_brand_state", "get_brand_context", "run_employee_meeting"]
        assert all(call.status == "completed" for call in calls)

        runs = client.get(f"/api/agent/brands/{brand_id}/runs")
        assert runs.status_code == 200, runs.text
        assert runs.json()[0]["status"] == "completed"
        assert [call["tool_name"] for call in runs.json()[0]["tool_calls"]] == [
            "get_brand_state",
            "get_brand_context",
            "run_employee_meeting",
        ]
    finally:
        db.close()


def test_agent_rejects_invalid_structured_proposal_without_mutation(client: TestClient, monkeypatch) -> None:
    signup(client, "agent-invalid@example.com")
    brand_id = create_brand(client)

    def invalid_response(self, skill_name, message, context):
        return LLMResponse(text="잘못된 제안", proposed_changes={"brand.not_allowed": "bad"})

    monkeypatch.setattr(agent_service.SkillExecutor, "execute", invalid_response)
    response = client.post(
        "/api/agent/chat",
        json={"brand_id": brand_id, "message": "일반적인 브랜드 설명을 해줘"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["proposal_id"] is None
    assert "Unsupported BrandState path" in response.json()["context"]["proposal_error"]
    state = client.get(f"/api/brands/{brand_id}/state").json()
    assert state["version"] == 1


def test_agent_research_request_creates_approval_pending_job(client: TestClient) -> None:
    signup(client, "agent-research@example.com")
    brand_id = create_brand(client)
    response = client.post(
        "/api/agent/chat",
        json={"brand_id": brand_id, "message": "우리 시장과 경쟁사를 조사해줘"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["route"] == "research"
    job_result = body["context"]["tool_results"]["create_research_job"]
    assert job_result["status"] == "planning"
    job = client.get(f"/api/research/jobs/{job_result['job_id']}")
    assert job.status_code == 200
    assert job.json()["status"] == "planning"
