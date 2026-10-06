from dataclasses import dataclass, field
from typing import Any

from app.skills.registry import SkillRegistry, skill_registry


@dataclass(frozen=True)
class EvaluationResult:
    sufficient: bool
    reason: str
    missing: list[str] = field(default_factory=list)
    recommended_action: str = "final"
    should_ask_user: bool = False
    waiting_for_approval: bool = False
    proposal_id: str | None = None
    pending_resource_id: str | None = None
    message: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "sufficient": self.sufficient,
            "reason": self.reason,
            "missing": self.missing,
            "recommended_action": self.recommended_action,
            "should_ask_user": self.should_ask_user,
            "waiting_for_approval": self.waiting_for_approval,
            "proposal_id": self.proposal_id,
            "pending_resource_id": self.pending_resource_id,
            "message": self.message,
        }


class AgentEvaluator:
    def __init__(self, registry: SkillRegistry = skill_registry) -> None:
        self.registry = registry

    def evaluate(
        self,
        goal: str,
        context: dict[str, Any],
        *,
        skill_name: str | None = None,
        tool_results: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        selected_skill = skill_name or self._select_skill(context)
        results = tool_results or context.get("agent", {}).get("tool_results", {})
        proposal_id = self._proposal_id(results, context)
        if proposal_id:
            return EvaluationResult(
                sufficient=True,
                reason="검토를 기다리는 Proposal이 있습니다.",
                recommended_action="wait_for_approval",
                waiting_for_approval=True,
                proposal_id=proposal_id,
                message="제안이 준비되었습니다. 승인 후 BrandState에 적용할 수 있습니다.",
            )

        research_result = results.get("create_research_job")
        if isinstance(research_result, dict) and research_result.get("status") != "completed":
            return EvaluationResult(
                sufficient=False,
                reason="Research Job이 아직 완료되지 않았습니다.",
                recommended_action="wait_for_approval",
                waiting_for_approval=True,
                pending_resource_id=research_result.get("job_id"),
                message="Research Job을 승인하고 실행한 뒤 결과를 확인하면 다음 단계를 진행할 수 있습니다.",
            )

        if selected_skill is None or selected_skill in {"conversation", "research"} and not self._requires_skill(goal):
            return EvaluationResult(sufficient=True, reason="추가 도구 없이 응답할 수 있습니다.")

        skill = self.registry.get(selected_skill)
        missing = self._missing_paths(skill.dependencies, context, context_root="brand_state")
        missing.extend(self._missing_sections(skill.required_context, context))
        if missing:
            return EvaluationResult(
                sufficient=False,
                reason=f"{selected_skill} 실행에 필요한 정보가 부족합니다.",
                missing=sorted(set(missing)),
                recommended_action="research" if any(item.startswith("market.") for item in missing) else "ask_user",
                should_ask_user=not any(item.startswith("market.") for item in missing),
                message="고객과 시장에 대한 정보를 알려주시면 다음 단계를 진행할 수 있습니다.",
            )
        return EvaluationResult(
            sufficient=True,
            reason="Skill 실행에 필요한 정보가 충분합니다.",
            recommended_action="propose" if skill.proposal_required else "final",
        )

    def _select_skill(self, context: dict[str, Any]) -> str | None:
        return context.get("selected_skill") or context.get("agent", {}).get("selected_skill")

    @staticmethod
    def _requires_skill(goal: str) -> bool:
        return any(keyword in goal.casefold() for keyword in ("브랜드", "포지셔닝", "고객", "시장", "조사", "research"))

    def _missing_paths(
        self,
        paths: tuple[str, ...],
        context: dict[str, Any],
        *,
        context_root: str | None = None,
    ) -> list[str]:
        missing: list[str] = []
        for path in paths:
            lookup = f"{context_root}.{path}" if context_root else path
            if self._is_empty(self._get_path(context, lookup)):
                missing.append(path)
        return missing

    def _missing_sections(self, sections: tuple[str, ...], context: dict[str, Any]) -> list[str]:
        brand_state = context.get("brand_state", {})
        return [section for section in sections if section not in brand_state]

    @staticmethod
    def _get_path(value: Any, path: str) -> Any:
        current = value
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    @staticmethod
    def _is_empty(value: Any) -> bool:
        return value is None or value == "" or value == [] or value == {}

    @staticmethod
    def _proposal_id(results: dict[str, Any], context: dict[str, Any]) -> str | None:
        for result in results.values():
            if isinstance(result, dict) and result.get("proposal_id"):
                return result["proposal_id"]
        proposals = context.get("pending_proposals", [])
        return proposals[0].get("id") if proposals and isinstance(proposals[0], dict) else None