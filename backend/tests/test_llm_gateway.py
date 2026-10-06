from types import SimpleNamespace

from app.llm.gemini import GeminiGateway


class FakeModels:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.response_text = "테스트 응답"

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self, models: FakeModels) -> None:
        self.models = models


def test_gemini_gateway_passes_model_prompt_and_system_instruction(monkeypatch) -> None:
    models = FakeModels()
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    response = gateway.generate_text(
        task="brand",
        message="포지셔닝을 정리해줘",
        context={"brand": {"name": "NAME TAG"}},
    )

    assert response.text == "테스트 응답"
    assert len(models.calls) == 1
    call = models.calls[0]
    assert call["model"] == "test-model"
    assert "포지셔닝을 정리해줘" in call["contents"]
    assert "NAME TAG" in call["config"].system_instruction
    assert call["config"].response_mime_type == "application/json"


def test_gemini_gateway_includes_conversation_history_in_prompt(monkeypatch) -> None:
    models = FakeModels()
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    GeminiGateway(api_key="test-key", model="test-model").generate_text(
        task="conversation",
        message="그 방향으로 이어서 정리해줘",
        context={"conversation_history": [{"role": "user", "content": "대학생용 서비스야"}]},
    )

    assert "대학생용 서비스야" in models.calls[0]["contents"]


def test_gemini_gateway_parses_structured_response() -> None:
    gateway = object.__new__(GeminiGateway)

    response = gateway._parse_response(
        '{"message":"정리했어요.","artifact_type":"brand_strategy",'
        '"artifact_content":{"positioning":"명확한 포지셔닝"}}'
    )

    assert response.text == "정리했어요."
    assert response.artifact_type == "brand_strategy"
    assert response.artifact_content["positioning"] == "명확한 포지셔닝"


def test_gemini_gateway_turns_direction_array_into_selectable_artifact() -> None:
    gateway = object.__new__(GeminiGateway)

    response = gateway._parse_response(
        '[{"direction":"Critical Builder","slogans":["문제를 해결합니다."],'
        '"keywords":["Impact"]}]'
    )

    assert response.text.startswith("세 가지 방향")
    assert response.artifact_type == "brand_direction_options"
    assert response.artifact_content["options"][0]["direction"] == "Critical Builder"


def test_gemini_gateway_parses_fenced_planner_aliases() -> None:
    gateway = object.__new__(GeminiGateway)

    decision = gateway._parse_json_object(
        '```json\n{"action":"tool_call","reason":"상태 확인",'
        '"tool":"get_brand_state","params":{}}\n```'
    )
    normalized = gateway._normalize_plan_payload(decision)

    assert normalized["tool_name"] == "get_brand_state"
    assert normalized["arguments"] == {}


def test_gemini_gateway_plan_agent_falls_back_with_parse_diagnostics(monkeypatch, caplog) -> None:
    models = FakeModels()
    models.response_text = "브랜드 상태를 확인할게요."
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    with caplog.at_level("ERROR"):
        decision = gateway.plan_agent("브랜드 상태를 보여줘", {}, [], [], {})

    assert decision.action == "ask_user"
    assert "Agent planner response parsing failed" in caplog.text