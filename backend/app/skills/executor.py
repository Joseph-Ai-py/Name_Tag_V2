from typing import Any

from app.llm.gateway import LLMGateway, get_llm_gateway
from app.llm.schemas import LLMResponse
from app.skills.registry import SkillRegistry, skill_registry


class SkillExecutor:
    def __init__(
        self,
        registry: SkillRegistry = skill_registry,
        gateway: LLMGateway | None = None,
    ) -> None:
        self.registry = registry
        self.gateway = gateway or get_llm_gateway()

    def execute(
        self,
        skill_name: str,
        message: str,
        context: dict[str, Any],
    ) -> LLMResponse:
        skill = self.registry.get(skill_name)
        response = self.gateway.generate_text(
            task=skill.task,
            message=message,
            context=context,
        )

        if skill.artifact_type is None or response.artifact_type is not None:
            return response

        return LLMResponse(
            text=response.text,
            artifact_type=skill.artifact_type,
            artifact_content={"response": response.text},
        )