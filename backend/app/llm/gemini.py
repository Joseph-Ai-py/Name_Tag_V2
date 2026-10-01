from typing import Any
import json

from google.genai import types

from app.llm.schemas import LLMResponse


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
