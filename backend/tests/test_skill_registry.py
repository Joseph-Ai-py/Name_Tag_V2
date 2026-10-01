import pytest

from app.llm.schemas import LLMResponse
from app.skills.executor import SkillExecutor
from app.skills.registry import SkillRegistry


class FakeGateway:
    def __init__(self) -> None:
        self.task = None

    def generate_text(self, task, message, context):
        self.task = task
        return LLMResponse(text="실행 결과")


def test_skill_executor_resolves_skill_and_delegates_to_gateway() -> None:
    gateway = FakeGateway()
    executor = SkillExecutor(SkillRegistry(), gateway)

    response = executor.execute(
        skill_name="customer",
        message="타겟을 정리해줘",
        context={"customer": {}},
    )

    assert response.text == "실행 결과"
    assert gateway.task == "customer"
    assert response.artifact_type == "customer_analysis"
    assert response.artifact_content == {"response": "실행 결과"}


def test_skill_registry_rejects_unknown_skill() -> None:
    with pytest.raises(ValueError, match="Unknown skill"):
        SkillRegistry().get("missing")