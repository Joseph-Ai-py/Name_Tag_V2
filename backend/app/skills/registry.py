from dataclasses import dataclass


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    task: str
    artifact_type: str | None = None


class SkillRegistry:
    def __init__(self) -> None:
        definitions = (
            SkillDefinition("conversation", "conversation"),
            SkillDefinition("research", "research", "market_research"),
            SkillDefinition("customer", "customer", "customer_analysis"),
            SkillDefinition("brand", "brand", "brand_strategy"),
            SkillDefinition("business", "business", "business_discovery"),
            SkillDefinition("visual", "visual", "visual_direction"),
        )
        self._definitions = {definition.name: definition for definition in definitions}

    def get(self, name: str) -> SkillDefinition:
        definition = self._definitions.get(name)
        if definition is None:
            raise ValueError(f"Unknown skill: {name}")
        return definition


skill_registry = SkillRegistry()