from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    task: str
    artifact_type: str | None = None
    description: str = ""
    purpose: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    required_context: tuple[str, ...] = ()
    optional_context: tuple[str, ...] = ()
    output_paths: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    risk_level: str = "low"
    proposal_required: bool = False


class SkillRegistry:
    def __init__(self) -> None:
        definitions = [
            SkillDefinition("conversation", "conversation"),
            SkillDefinition("research", "research", "market_research"),
            SkillDefinition("customer", "customer", "customer_analysis"),
            SkillDefinition("brand", "brand", "brand_strategy"),
            SkillDefinition("business", "business", "business_discovery"),
            SkillDefinition("visual", "visual", "visual_direction"),
        ]
        definitions.extend(_domain_skill_definitions())
        self._definitions = {definition.name: definition for definition in definitions}

    def get(self, name: str) -> SkillDefinition:
        definition = self._definitions.get(name)
        if definition is None:
            raise ValueError(f"Unknown skill: {name}")
        return definition

    def domain_names(self) -> tuple[str, ...]:
        base_names = {"conversation", "research", "customer", "brand", "business", "visual"}
        return tuple(sorted(name for name in self._definitions if name not in base_names))

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))


def _domain_skill_definitions() -> list[SkillDefinition]:
    return [
        SkillDefinition("discover_brand_interview", "discover_brand_interview", "brand_discovery", "Legacy O discovery interview", "Find missing brand inputs", required_context=("business", "customer", "brand")),
        SkillDefinition("generate_brand_candidates", "generate_brand_candidates", "brand_candidates", "Legacy O MVB candidates", "Generate selectable brand foundations", required_context=("business", "customer"), output_paths=("brand.name", "brand.tagline", "brand.story")),
        SkillDefinition("select_brand_candidate", "select_brand_candidate", "brand_selection", "Legacy O candidate composition", "Compose user-selected candidate fields", required_context=("brand_candidates",), output_paths=("brand.name", "brand.tagline", "brand.story"), proposal_required=True),
        SkillDefinition("generate_brand_philosophy", "generate_brand_philosophy", "brand_philosophy", "Legacy A1 philosophy and identity", "Generate philosophy, essence, and core identity", required_context=("brand", "conversation_history"), output_paths=("brand.mission", "brand.vision", "brand.values"), proposal_required=True),
        SkillDefinition("generate_brand_story", "generate_brand_story", "brand_story", "Legacy A2 story expansion", "Expand naming, slogans, and brand story", required_context=("brand",), dependencies=("brand.story",), output_paths=("brand.story",), proposal_required=True),
        SkillDefinition("generate_positioning", "generate_positioning", "positioning_analysis", "Legacy A3 positioning", "Generate positioning and brand promise", required_context=("brand", "customer", "market"), dependencies=("customer.target", "market.competitors"), output_paths=("brand.positioning",), risk_level="medium", proposal_required=True),
        SkillDefinition("generate_persona", "generate_persona", "persona_analysis", "Legacy B1 persona", "Generate primary and secondary personas", required_context=("brand", "customer", "business"), output_paths=("customer.persona",), proposal_required=True),
        SkillDefinition("generate_customer_journey", "generate_customer_journey", "customer_journey", "Legacy B2 journey", "Generate customer journey and funnel", required_context=("brand", "customer"), dependencies=("customer.persona",), output_paths=("customer.journey",), proposal_required=True),
        SkillDefinition("analyze_customer_swot", "analyze_customer_swot", "customer_swot", "Legacy B4 customer SWOT", "Analyze customer strengths and risks", required_context=("brand", "customer", "market"), output_paths=("market.swot",), proposal_required=True),
        SkillDefinition("generate_business_model", "generate_business_model", "business_model", "Legacy B5 business model", "Generate business model and hypotheses", required_context=("brand", "customer", "business"), dependencies=("customer.persona",), output_paths=("business.business_model",), proposal_required=True),
        SkillDefinition("generate_visual_identity", "generate_visual_identity", "visual_identity", "Legacy C1 visual identity", "Generate colors, typography, mood, and principles", required_context=("brand", "visual"), output_paths=("visual.colors", "visual.typography", "visual.mood"), proposal_required=True),
        SkillDefinition("generate_logo_identity", "generate_logo_identity", "logo_identity", "Legacy DE logo identity", "Generate logo concept and usage guide", required_context=("brand", "visual", "customer"), dependencies=("brand.positioning", "visual.colors"), output_paths=("visual.logo",), proposal_required=True),
        SkillDefinition("generate_character_guide", "generate_character_guide", "character_guide", "Legacy DE character guide", "Generate character identity and story", required_context=("brand", "visual", "customer"), output_paths=("visual.character",), proposal_required=True),
        SkillDefinition("regenerate_brand_field", "regenerate_brand_field", "field_candidates", "Legacy field regeneration", "Generate three alternatives for one selected field", required_context=("brand",), risk_level="low"),
    ]


skill_registry = SkillRegistry()