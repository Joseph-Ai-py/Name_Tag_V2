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


def test_gemini_gateway_accepts_developer_api_planner_payload(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = '{"action":"tool_call","tool_name":"get_brand_state","input":{}}'
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("브랜드 상태를 보여줘", {}, [], [], {})

    assert decision.action == "tool_call"
    assert decision.tool_name == "get_brand_state"
    assert decision.arguments == {}
    assert "response_schema" not in models.calls[0]["config"]


def test_gemini_gateway_treats_final_input_as_message(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = '{"action":"final","input":"완료된 답변입니다."}'
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("안녕하세요", {}, [], [], {})

    assert decision.action == "final"
    assert decision.message == "완료된 답변입니다."


def test_gemini_gateway_extracts_content_from_structured_final_input(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = '{"action":"final","input":{"content":"대화 답변입니다."}}'
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("안녕하세요", {}, [], [], {})

    assert decision.action == "final"
    assert decision.message == "대화 답변입니다."


def test_gemini_gateway_accepts_final_output_as_message(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = '{"action":"final","thought":"인사에 답합니다.","output":"반갑습니다."}'
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("안녕하세요", {}, [], [], {})

    assert decision.action == "final"
    assert decision.reason == "인사에 답합니다."
    assert decision.message == "반갑습니다."


def test_gemini_gateway_prefers_final_output_over_echoed_input(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '{"action":"final","input":"지금 내 브랜드는 뭐야?",'
        '"output":"현재 브랜드는 AI Product Builder입니다."}'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("지금 내 브랜드는 뭐야?", {}, [], [], {})

    assert decision.message == "현재 브랜드는 AI Product Builder입니다."


def test_gemini_gateway_extracts_message_from_object_output(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '{"action":"final","input":{"goal":"내 브랜드 포지셔닝은 뭐야?"},'
        '"output":{"message":"현재 포지셔닝은 기술을 비즈니스 가치로 전환하는 엔드투엔드 해결사입니다."}}'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("내 브랜드 포지셔닝은 뭐야?", {}, [], [], {})

    assert decision.message == "현재 포지셔닝은 기술을 비즈니스 가치로 전환하는 엔드투엔드 해결사입니다."


def test_gemini_gateway_accepts_single_decision_array(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '[{"action":"final","input":{"message":"브랜드 Overview 초안입니다."}}]'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("브랜드 Overview를 작성해줘", {}, [], [], {})

    assert decision.action == "final"
    assert decision.message == "브랜드 Overview 초안입니다."


def test_gemini_gateway_parses_proposal_payload(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '[{"action":"propose","input":{"title":"브랜드 정교화",'
        '"summary":"브랜드 정체성을 업데이트합니다.",'
        '"changes":{"brand.positioning":"기술을 가치로 전환하는 전문가"}}}]'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("브랜드를 개선해줘", {}, [], [], {})

    assert decision.action == "propose"
    assert decision.proposal_title == "브랜드 정교화"
    assert decision.proposal_summary == "브랜드 정체성을 업데이트합니다."
    assert decision.proposed_changes == {"brand.positioning": "기술을 가치로 전환하는 전문가"}


def test_gemini_gateway_parses_wait_for_approval_input(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '[{"action":"wait_for_approval","input":{"proposal_id":"proposal-1",'
        '"message":"제안을 승인해 주세요."}}]'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("제안을 적용해줘", {}, [], [], {})

    assert decision.action == "wait_for_approval"
    assert decision.proposal_id == "proposal-1"
    assert decision.message == "제안을 승인해 주세요."


def test_gemini_gateway_accepts_decision_alias_for_action(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '[{"decision":"final","message":"다시 확인해 보겠습니다."}]'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("다시 해봐", {}, [], [], {})

    assert decision.action == "final"
    assert decision.reason == "다시 확인해 보겠습니다."
    assert decision.message == "다시 확인해 보겠습니다."


def test_gemini_gateway_parses_nested_tool_call_command(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '{"action":"tool_call","tool_call":{"command":"create_research_job",'
        '"parameters":{"query":"시장 규모 분석"}}}'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("시장 규모를 조사해줘", {}, [], [], {})

    assert decision.action == "tool_call"
    assert decision.tool_name == "create_research_job"
    assert decision.arguments == {"query": "시장 규모 분석"}


def test_gemini_gateway_parses_tool_call_inside_input(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '{"action":"tool_call","input":{"tool_name":"create_research_job",'
        '"tool_input":{"query":"TAM SAM SOM 분석"}}}'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("시장 규모를 조사해줘", {}, [], [], {})

    assert decision.action == "tool_call"
    assert decision.tool_name == "create_research_job"
    assert decision.arguments == {"query": "TAM SAM SOM 분석"}


def test_gemini_gateway_parses_named_nested_tool_call_with_plan(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '[{"action":"tool_call","tool_call":{"name":"create_research_job",'
        '"arguments":{"query":"시장 규모 분석","plan":{"steps":["시장 조사"]}}}}]'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("시장 규모를 조사해줘", {}, [], [], {})

    assert decision.action == "tool_call"
    assert decision.tool_name == "create_research_job"
    assert decision.arguments["plan"]["steps"] == ["시장 조사"]


def test_gemini_gateway_inferrs_tool_call_action_when_omitted(monkeypatch) -> None:
    models = FakeModels()
    models.response_text = (
        '[{"tool_call":{"name":"create_research_job",'
        '"arguments":{"query":"시장 분석"}}}]'
    )
    monkeypatch.setattr(
        "google.genai.Client",
        lambda api_key: FakeClient(models),
    )

    gateway = GeminiGateway(api_key="test-key", model="test-model")
    decision = gateway.plan_agent("시장 분석을 해줘", {}, [], [], {})

    assert decision.action == "tool_call"
    assert decision.tool_name == "create_research_job"
    assert decision.arguments == {"query": "시장 분석"}


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