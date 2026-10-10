import pytest
from pydantic import ValidationError

from app.agent.context_manager import build_context
from app.agent.core import AgentCore
from app.agent.evaluator import AgentEvaluator
from app.agent.planner import AgentPlanner
from app.agent.state import AgentBudget, AgentDecision, AgentExecutionState
from app.agent.validation import AgentToolValidator
from app.llm.gateway import MockLLMGateway


def test_agent_decision_requires_action_specific_fields() -> None:
    with pytest.raises(ValidationError):
        AgentDecision(action="tool_call", reason="missing tool")
    with pytest.raises(ValidationError):
        AgentDecision(action="ask_user", reason="missing message")
    with pytest.raises(ValidationError):
        AgentDecision(action="wait_for_approval", reason="missing resource")


def test_context_contains_workspace_state_without_backend_identity() -> None:
    context = build_context(
        {"brand": {"positioning": "clear"}},
        version=4,
        conversation_history=[{"role": "user", "content": "hello"}],
        user_role="editor",
        goal="포지셔닝",
    )

    assert context["brand_state"]["version"] == 4
    assert context["conversation"]["recent_messages"][0]["content"] == "hello"
    assert context["user"]["role"] == "editor"
    assert "brand_id" not in context
    assert "user_id" not in context


def test_positioning_evaluation_reports_missing_dependencies() -> None:
    context = build_context(
        {"customer": {"target": None}, "market": {"competitors": []}},
        goal="포지셔닝 개선",
    )
    result = AgentEvaluator().evaluate(
        "포지셔닝 개선",
        context,
        skill_name="generate_positioning",
    )

    assert result.sufficient is False
    assert set(result.missing) == {"customer.target", "market.competitors"}
    assert result.recommended_action == "research"


def test_research_job_evaluation_waits_for_completion() -> None:
    context = build_context({}, goal="시장 조사")
    result = AgentEvaluator().evaluate(
        "시장 조사",
        context,
        skill_name="research",
        tool_results={"create_research_job": {"job_id": "job-1", "status": "planning"}},
    )

    assert result.waiting_for_approval is True
    assert result.pending_resource_id == "job-1"


def test_tool_validator_rejects_invalid_arguments_and_backend_identity() -> None:
    validator = AgentToolValidator()
    validator.validate("create_research_job", {"query": "경쟁사"}, "editor")

    with pytest.raises(ValueError):
        validator.validate("create_research_job", {}, "editor")
    with pytest.raises(ValueError):
        validator.validate(
            "create_research_job",
            {"query": "경쟁사", "brand_id": "other-brand"},
            "editor",
        )
    with pytest.raises(PermissionError):
        validator.validate("create_document", {"title": "draft"}, "viewer")
    with pytest.raises(PermissionError):
        validator.validate("apply_brand_change", {"proposal_id": "p-1"}, "editor")


def test_mock_planner_can_receive_deterministic_decisions() -> None:
    planner = MockLLMGateway(
        decisions=[AgentDecision(action="final", reason="test", confidence=1.0)]
    )

    decision = planner.plan_agent("hello", {}, [], [], {})

    assert decision.action == "final"
    assert decision.confidence == 1.0


def test_planner_gateway_failure_is_recorded_on_execution_state() -> None:
    class FailingGateway:
        def plan_agent(self, **kwargs):
            raise TimeoutError("planner timed out")

    state = AgentExecutionState(
        goal="hello",
        mode="simple",
        route="conversation",
        budget=AgentBudget(),
    )

    decision = AgentPlanner(FailingGateway()).decide("hello", {}, state, [], [], {})

    assert decision.action == "ask_user"
    assert state.failure_code == "planner_gateway_error"
    assert state.failure_stage == "planner"
    assert state.failure_type == "TimeoutError"


