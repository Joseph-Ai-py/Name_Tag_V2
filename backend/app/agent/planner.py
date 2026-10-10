from typing import Any
import logging

from app.agent.state import AgentDecision, AgentExecutionState
from app.llm.gateway import LLMGateway, get_llm_gateway


logger = logging.getLogger(__name__)


class AgentPlanner:
    def __init__(self, gateway: LLMGateway | None = None) -> None:
        self.gateway = gateway or get_llm_gateway()

    def decide(
        self,
        goal: str,
        context: dict[str, Any],
        state: AgentExecutionState,
        tools: list[dict[str, Any]],
        skills: list[dict[str, Any]],
        evaluation: dict[str, Any],
    ) -> AgentDecision:
        try:
            decision = self.gateway.plan_agent(
                goal=goal,
                context=context,
                tools=tools,
                skills=skills,
                evaluation=evaluation,
            )
        except Exception as exc:
            logger.exception("Agent planner gateway failed")
            self._record_failure(state, "planner_gateway_error", exc)
            return AgentDecision(
                action="ask_user",
                reason="Planner gateway 호출에 실패했습니다.",
                message="요청을 처리하지 못했습니다. 잠시 후 다시 시도해주세요.",
            )
        if not isinstance(decision, AgentDecision):
            logger.error("Planner returned unexpected decision type: %r", type(decision))
            self._record_failure(
                state,
                "planner_invalid_result",
                TypeError(f"unexpected decision type: {type(decision).__name__}"),
            )
            return AgentDecision(
                action="ask_user",
                reason="Planner 결과 형식이 올바르지 않습니다.",
                message="요청을 안전하게 판단하지 못했습니다.",
            )
        if decision.action == "ask_user" and decision.reason.startswith("Planner 응답을 검증할 수 없습니다"):
            self._record_failure(state, "planner_response_invalid", ValueError(decision.reason))
        return decision

    @staticmethod
    def _record_failure(
        state: AgentExecutionState,
        code: str,
        error: Exception,
    ) -> None:
        state.failure_code = code
        state.failure_stage = "planner"
        state.failure_type = type(error).__name__