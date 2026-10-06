from app.llm.schemas import LLMResponse
from app.skills.domain import normalize_domain_response
from app.skills.executor import SkillExecutor
from app.skills.registry import SkillRegistry
from app.services.agent_service import _select_skill


def test_legacy_domain_skill_library_is_registered_with_dependencies() -> None:
    registry = SkillRegistry()

    positioning = registry.get("generate_positioning")
    assert positioning.required_context == ("brand", "customer", "market")
    assert positioning.dependencies == ("customer.target", "market.competitors")
    assert positioning.output_paths == ("brand.positioning",)
    assert positioning.proposal_required is True

    assert "generate_brand_candidates" in registry.domain_names()
    assert "generate_visual_identity" in registry.domain_names()
    assert "generate_logo_identity" in registry.domain_names()


def test_legacy_positioning_output_maps_to_v2_brand_state() -> None:
    response = normalize_domain_response(
        "generate_positioning",
        LLMResponse(
            text="포지셔닝을 생성했습니다.",
            artifact_content={"positioning": {"statement": "명확한 브랜드"}},
        ),
    )

    assert response.proposed_changes == {
        "brand.positioning": {"statement": "명확한 브랜드"},
    }


def test_domain_skill_does_not_overwrite_existing_proposal() -> None:
    response = normalize_domain_response(
        "generate_positioning",
        LLMResponse(
            text="기존 제안",
            proposed_changes={"brand.positioning": "기존 제안"},
        ),
    )

    assert response.proposed_changes == {"brand.positioning": "기존 제안"}


def test_agent_selects_domain_skill_without_section_pipeline() -> None:
    assert _select_skill("brand", "포지셔닝을 다시 만들어줘") == "generate_positioning"
    assert _select_skill("customer", "페르소나를 만들어줘") == "generate_persona"
    assert _select_skill("visual", "새 로고를 만들어줘") == "generate_logo_identity"


class DomainGateway:
    def __init__(self) -> None:
        self.task = None
        self.message = None

    def generate_text(self, task, message, context):
        self.task = task
        self.message = message
        return LLMResponse(
            text="포지셔닝 결과",
            artifact_content={"positioning": {"statement": "명확한 방향"}},
        )


def test_domain_skill_executor_adapts_prompt_and_normalizes_output() -> None:
    gateway = DomainGateway()
    response = SkillExecutor(SkillRegistry(), gateway).execute(
        "generate_positioning",
        "포지셔닝을 만들어줘",
        {"brand": {}, "customer": {}, "market": {}},
    )

    assert gateway.task == "generate_positioning"
    assert "Legacy A3" in gateway.message
    assert response.proposed_changes == {
        "brand.positioning": {"statement": "명확한 방향"},
    }