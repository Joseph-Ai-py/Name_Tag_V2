from typing import Any

from app.llm.gateway import LLMGateway, get_llm_gateway
from app.llm.schemas import LLMResponse
from app.skills.domain import build_domain_prompt, normalize_domain_response
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
        prompt = message
        if skill_name in skill_registry.domain_names():
            prompt = build_domain_prompt(skill_name, message, context)
        response = self.gateway.generate_text(
            task=skill.task,
            message=prompt,
            context=context,
        )

        if skill.artifact_type is None:
            return normalize_domain_response(skill_name, response)

        if response.artifact_type is None:
            response = LLMResponse(
                text=response.text,
                artifact_type=skill.artifact_type,
                artifact_content=response.artifact_content or {"response": response.text},
                proposed_changes=response.proposed_changes,
            )
        return normalize_domain_response(skill_name, response)