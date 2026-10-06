from typing import Any

from app.agent.state import AgentDecision, AgentExecutionState
from app.llm.gateway import LLMGateway, get_llm_gateway


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
        decision = self.gateway.plan_agent(
            goal=goal,
            context=context,
            tools=tools,
            skills=skills,
            evaluation=evaluation,
        )
        if not isinstance(decision, AgentDecision):
            return AgentDecision(
                action="ask_user",
                reason="Planner 결과 형식이 올바르지 않습니다.",
                message="요청을 안전하게 판단하지 못했습니다.",
            )
        return decision