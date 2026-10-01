from typing import Any

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
			"Respond in Korean and provide a concise next step.\n"
			f"Task: {task}\n"
			f"Brand context: {context}\n"
			f"User request: {message}"
		)
		response = self.client.models.generate_content(
			model=self.model,
			contents=prompt,
		)
		text = response.text or "요청을 처리했어요. 다음 작업을 정리해볼게요."
		return LLMResponse(text=text)
