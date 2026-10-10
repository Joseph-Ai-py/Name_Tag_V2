from typing import Any
import json
import logging

from google.genai import types

from app.agent.state import AgentDecision
from app.llm.schemas import LLMPlanResponse, LLMResponse


logger = logging.getLogger(__name__)


class GeminiGateway:
	def __init__(self, api_key: str | None, model: str) -> None:
		if not api_key:
			raise RuntimeError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")

		from google import genai

		self.client = genai.Client(api_key=api_key)
		self.model = model

	def generate_text(
		self,
		task: str,
		message: str,
		context: dict[str, Any],
	) -> LLMResponse:
		prompt = (
			"You are the NAME TAG brand workspace assistant. "
			"Respond in Korean, preserve the user's intent, and provide a concise next step.\n"
			"Return only valid JSON with keys message, artifact_type, and artifact_content. "
			"Use null for artifact_type when no artifact is needed.\n"
			"Conversation history is authoritative context. Refer to it when the user says "
			"it, that, earlier, or otherwise relies on previous messages.\n"
			f"Task: {task}\n"
			f"Brand context: {context}\n"
			f"User request: {message}"
		)
		response = self.client.models.generate_content(
			model=self.model,
			contents=prompt,
			config=types.GenerateContentConfig(
				response_mime_type="application/json",
				system_instruction=(
					"NAME TAG는 사용자의 사업과 브랜드를 함께 발전시키는 AI Brand Workspace입니다. "
					"근거 없는 사실이나 수치를 확정적으로 만들지 말고, 필요한 경우 추가 질문을 하세요."
				),
			),
		)
		text = response.text or "요청을 처리했어요. 다음 작업을 정리해볼게요."
		return self._parse_response(text)

	def plan_agent(
		self,
		goal: str,
		context: dict[str, Any],
		tools: list[dict[str, Any]],
		skills: list[dict[str, Any]],
		evaluation: dict[str, Any],
	) -> AgentDecision:
		prompt = (
			"You are the planning engine of NAME TAG. Return only valid JSON. "
			"Choose exactly one action: tool_call, final, ask_user, propose, replan, wait_for_approval. "
			"Treat greetings, thanks, acknowledgements, casual questions, and requests for explanation as conversation: "
			"choose final and put the answer in message, input, or output. "
			"Choose tool_call, propose, or wait_for_approval only when the user explicitly asks for research, generation, "
			"analysis, or a brand/workspace change that needs execution. "
			"Never invent user_id, brand_id, role, database access, or approval. "
			"Never apply a BrandState change; create a proposal and wait for approval.\n"
			f"Goal: {goal}\nContext: {context}\nEvaluation: {evaluation}\n"
			f"Available tools: {tools}\nAvailable skills: {skills}"
		)
		response = self.client.models.generate_content(
			model=self.model,
			contents=prompt,
			config=types.GenerateContentConfig(
				response_mime_type="application/json",
				system_instruction="NAME TAG planner must make one safe next-action decision.",
			),
		)
		try:
			raw_text = response.text or ""
			logger.info("Planner response received (%d chars)", len(raw_text))
			payload = self._parse_json_object(raw_text)
			payload = self._normalize_plan_payload(payload)
			decision = LLMPlanResponse.model_validate(payload).to_decision()
			logger.info("PARSED PLANNER DECISION: %r / type=%s", decision, type(decision).__name__)
			return decision
		except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as exc:
			logger.exception("Agent planner response parsing failed")
			return AgentDecision(
				action="ask_user",
				reason=f"Planner 응답을 검증할 수 없습니다: {type(exc).__name__}",
				message="요청을 안전하게 판단하지 못했습니다. 필요한 작업을 조금 더 구체적으로 알려주세요.",
			)

	@staticmethod
	def _parse_json_object(text: str) -> dict[str, Any]:
		candidate = text.strip()
		if candidate.startswith("```"):
			candidate = candidate.split("\n", 1)[1] if "\n" in candidate else candidate
			candidate = candidate.rsplit("```", 1)[0].strip()
		try:
			payload = json.loads(candidate)
		except json.JSONDecodeError:
			start = candidate.find("{")
			if start < 0:
				raise
			payload, _ = json.JSONDecoder().raw_decode(candidate[start:])
		if isinstance(payload, list) and len(payload) == 1 and isinstance(payload[0], dict):
			payload = payload[0]
		if not isinstance(payload, dict):
			raise TypeError("Planner response must be a JSON object")
		return payload

	@staticmethod
	def _normalize_plan_payload(payload: dict[str, Any]) -> dict[str, Any]:
		aliases = {
			"decision": "action",
			"tool": "tool_name",
			"params": "arguments",
			"parameters": "arguments",
			"skill": "skill_name",
			"proposal": "proposal_id",
			"resource_id": "pending_resource_id",
		}
		normalized = dict(payload)
		if not normalized.get("action") and isinstance(normalized.get("tool_call"), dict):
			normalized["action"] = "tool_call"
		for source, target in aliases.items():
			if target not in normalized and source in normalized:
				normalized[target] = normalized.pop(source)
		if normalized.get("action") == "tool_call" and isinstance(normalized.get("tool_call"), dict):
			tool_call = normalized["tool_call"]
			normalized.setdefault("tool_name", tool_call.get("tool_name") or tool_call.get("command") or tool_call.get("name"))
			normalized.setdefault("arguments", tool_call.get("arguments") or tool_call.get("parameters") or tool_call.get("params") or {})
			normalized.pop("tool_call")
		if normalized.get("action") == "tool_call" and isinstance(normalized.get("input"), dict):
			tool_input = normalized["input"]
			normalized.setdefault("tool_name", tool_input.get("tool_name") or tool_input.get("command") or tool_input.get("name"))
			normalized.setdefault("arguments", tool_input.get("tool_input") or tool_input.get("arguments") or tool_input.get("parameters") or {})
		if normalized.get("action") != "tool_call" and "message" not in normalized:
			for source in ("output", "response"):
				value = normalized.get(source)
				if isinstance(value, dict):
					value = value.get("message") or value.get("content")
				if isinstance(value, str):
					normalized["message"] = value
					normalized.pop(source)
					break
		if normalized.get("action") == "propose" and isinstance(normalized.get("input"), dict):
			proposal = normalized["input"]
			normalized.setdefault("proposal_title", proposal.get("title"))
			normalized.setdefault("proposal_summary", proposal.get("summary"))
			normalized.setdefault("proposed_changes", proposal.get("changes"))
			normalized.setdefault("message", proposal.get("summary"))
		if normalized.get("action") == "wait_for_approval" and isinstance(normalized.get("input"), dict):
			approval = normalized["input"]
			normalized.setdefault("proposal_id", approval.get("proposal_id"))
			normalized.setdefault("pending_resource_id", approval.get("pending_resource_id"))
			normalized.setdefault("message", approval.get("message") or approval.get("content"))
		if not normalized.get("reason") and isinstance(normalized.get("thought"), str):
			normalized["reason"] = normalized["thought"]
		if "input" in normalized:
			target = "arguments" if normalized.get("action") == "tool_call" else "message"
			if target not in normalized:
				value = normalized["input"]
				if target == "message" and isinstance(value, dict):
					value = value.get("content") or value.get("message") or json.dumps(value, ensure_ascii=False)
				normalized[target] = value
			normalized.pop("input")
		if not normalized.get("reason") and isinstance(normalized.get("message"), str):
			normalized["reason"] = normalized["message"][:500]
		if isinstance(normalized.get("message"), dict):
			value = normalized["message"]
			normalized["message"] = value.get("content") or value.get("message") or json.dumps(value, ensure_ascii=False)
		if not normalized.get("reason") and normalized.get("action"):
			normalized["reason"] = f"Planner가 {normalized['action']} 작업을 선택했습니다."
		return normalized

	def _parse_response(self, text: str) -> LLMResponse:
		try:
			payload = json.loads(text)
		except json.JSONDecodeError:
			return LLMResponse(text=text)

		if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
			return LLMResponse(
				text="세 가지 방향을 제안했어요. 가장 가까운 방향을 선택해보세요.",
				artifact_type="brand_direction_options",
				artifact_content={"options": payload},
			)

		if not isinstance(payload, dict):
			return LLMResponse(text=text)

		message = payload.get("message")
		artifact_type = payload.get("artifact_type")
		artifact_content = payload.get("artifact_content", {})
		if artifact_type is None:
			for option_key in ("options", "directions", "recommendations"):
				if isinstance(payload.get(option_key), list):
					return LLMResponse(
						text="추천 방향을 정리했어요. 가장 가까운 방향을 선택해보세요.",
						artifact_type="brand_direction_options",
						artifact_content={option_key: payload[option_key]},
					)
		if not isinstance(message, str):
			return LLMResponse(text=text)
		if not isinstance(artifact_type, str) and artifact_type is not None:
			artifact_type = None
		if not isinstance(artifact_content, dict):
			artifact_content = {"value": artifact_content}

		return LLMResponse(
			text=message,
			artifact_type=artifact_type,
			artifact_content=artifact_content,
		)
