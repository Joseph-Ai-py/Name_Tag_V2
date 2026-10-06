from functools import lru_cache
from typing import Any, Protocol

from app.config import get_settings
from app.agent.state import AgentDecision
from app.llm.schemas import LLMResponse


class LLMGateway(Protocol):
	def generate_text(
		self,
		task: str,
		message: str,
		context: dict[str, Any],
	) -> LLMResponse:
		...

	def plan_agent(
		self,
		goal: str,
		context: dict[str, Any],
		tools: list[dict[str, Any]],
		skills: list[dict[str, Any]],
		evaluation: dict[str, Any],
	) -> AgentDecision:
		...


class MockLLMGateway:
	def __init__(self, decisions: list[AgentDecision] | None = None) -> None:
		self.decisions = list(decisions or [])
	responses = {
		"research": (
			"시장과 경쟁사 정보를 조사할 준비를 했어요. 먼저 조사 범위를 정해볼게요.",
			"market_research",
			"research_plan",
		),
		"customer": (
			"고객과 타겟을 정리할 준비를 했어요. 현재 고객 가설을 구체화해볼게요.",
			"customer_analysis",
			"define_customer",
		),
		"brand": (
			"브랜드 전략 결과를 만들 준비를 했어요. 핵심 메시지와 포지셔닝을 정리해볼게요.",
			"brand_strategy",
			"define_positioning",
		),
		"business": (
			"사업 구조를 정리할 준비를 했어요. 문제와 해결책의 관계를 확인해볼게요.",
			"business_discovery",
			"define_problem_solution",
		),
		"visual": (
			"비주얼 방향을 정리할 준비를 했어요. 브랜드 성격과 시각 요소를 연결해볼게요.",
			"visual_direction",
			"define_visual_direction",
		),
	}

	def generate_text(self, task: str, message: str, context: dict[str, Any]) -> LLMResponse:
		response = self.responses.get(task)
		if response is None:
			return LLMResponse(
				text="좋아요. 현재 브랜드 맥락을 유지하면서 다음 작업을 함께 정리해볼게요.",
			)

		text, artifact_type, next_step = response
		proposed_changes = None
		if task == "brand":
			proposed_changes = {
				"brand.positioning": "복잡한 브랜드 결정을 선명한 실행으로 연결하는 workspace",
			}
		return LLMResponse(
			text=text,
			artifact_type=artifact_type,
			artifact_content={
				"request": message,
				"next_step": next_step,
				"brand": {"positioning": proposed_changes["brand.positioning"]} if proposed_changes else {},
			},
			proposed_changes=proposed_changes,
		)

	def plan_agent(
		self,
		goal: str,
		context: dict[str, Any],
		tools: list[dict[str, Any]],
		skills: list[dict[str, Any]],
		evaluation: dict[str, Any],
	) -> AgentDecision:
		if self.decisions:
			return self.decisions.pop(0)

		available_tools = {item["name"] for item in tools}
		completed = set(context.get("agent", {}).get("completed_steps", []))
		missing = evaluation.get("missing", [])
		goal_lower = goal.casefold()
		if (
			"get_brand_state" in completed
			and "get_brand_context" in available_tools
			and "get_brand_context" not in completed
			and any(keyword in goal_lower for keyword in ("브랜드", "포지셔닝", "positioning"))
		):
			return AgentDecision(
				action="tool_call",
				tool_name="get_brand_context",
				arguments={"task": "brand_strategy"},
				reason="요청에 필요한 브랜드 맥락을 확인합니다.",
			)
		if evaluation.get("should_ask_user"):
			return AgentDecision(
				action="ask_user",
				reason=evaluation.get("reason", "필요한 정보가 부족합니다."),
				message=evaluation.get("message", "작업을 진행하기 위해 필요한 정보를 알려주세요."),
			)
		if "brand_state" not in context.get("agent", {}).get("observed", {}) and "get_brand_state" in available_tools:
			return AgentDecision(action="tool_call", tool_name="get_brand_state", reason="현재 BrandState를 먼저 확인합니다.")
		if (
			("research" in goal_lower or "조사" in goal_lower or "경쟁사" in goal_lower)
			and "create_research_job" in available_tools
			and "create_research_job" not in completed
		):
			return AgentDecision(action="tool_call", tool_name="create_research_job", arguments={"query": goal}, reason="부족한 근거를 조사합니다.")
		if evaluation.get("waiting_for_approval"):
			proposal_id = evaluation.get("proposal_id")
			pending_resource_id = proposal_id or evaluation.get("pending_resource_id")
			return AgentDecision(
				action="wait_for_approval",
				proposal_id=proposal_id if evaluation.get("recommended_action") == "wait_for_approval" and evaluation.get("proposal_id") else None,
				pending_resource_id=pending_resource_id,
				reason="생성된 제안은 사용자 승인이 필요합니다.",
				message="제안이 준비되었습니다. 승인 후 적용할 수 있습니다.",
			)
		return AgentDecision(action="final", reason="현재 정보로 응답을 생성할 수 있습니다.")


@lru_cache
def get_llm_gateway() -> LLMGateway:
	settings = get_settings()
	if settings.llm_provider == "gemini":
		from app.llm.gemini import GeminiGateway

		return GeminiGateway(
			api_key=settings.gemini_api_key,
			model=settings.gemini_model,
		)
	return MockLLMGateway()
