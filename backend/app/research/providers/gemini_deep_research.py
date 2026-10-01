from dataclasses import dataclass, field
from typing import Any

from google.genai import types

from app.config import get_settings


@dataclass
class ResearchSourceResult:
	url: str
	title: str
	publisher: str | None = None
	summary: str | None = None


@dataclass
class DeepResearchResult:
	text: str
	sources: list[ResearchSourceResult] = field(default_factory=list)
	raw: dict[str, Any] = field(default_factory=dict)


class GeminiDeepResearchProvider:
	def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
		settings = get_settings()
		if not api_key:
			api_key = settings.gemini_api_key
		if not api_key:
			raise RuntimeError("GEMINI_API_KEY is required for Deep Research")
		from google import genai

		self.client = genai.Client(api_key=api_key)
		self.model = model or settings.gemini_model

	def run(self, query: str, plan: dict[str, Any]) -> DeepResearchResult:
		project_context = (
			"NAME TAG는 초기 창업자와 1인 사업자를 위한 AI Micro Branding Workspace입니다. "
			"현재 저장소의 확인된 기술 범위는 FastAPI/Python Backend, React/TypeScript/Vite Frontend, "
			"Gemini LLM Gateway, BrandState, Agent, Skills, Tools, Conversation, Artifact, Research, "
			"Block Document, Asset, JSON Export입니다. 기존 O/A/B/C/DE 기능은 브랜드 발견·전략·고객·비주얼·에셋을 위한 내부 흐름입니다. "
			"이미지 자동 태깅, Computer Vision, Feature Store, CTR/Accuracy 성과, 실제 사용자 수치와 같은 사실은 이 프로젝트에서 확인되지 않았습니다."
		)
		prompt = (
			"Perform a deep research task for NAME TAG. Respond in Korean. "
			"Use web search and cite the sources you used. Do not invent project facts, metrics, users, "
			"technologies, architecture, or business results. Clearly label verified repository facts, "
			"external facts, analysis, assumptions, and recommendations. If evidence is unavailable, say so.\n"
			f"Verified project context: {project_context}\n"
			f"Research query: {query}\nResearch plan: {plan}\n"
			"Required report sections: Executive Summary, Verified Facts, External Sources, Analysis, "
			"Recommendations, Uncertainties and Limitations."
		)
		response = self.client.models.generate_content(
			model=self.model,
			contents=prompt,
			config=types.GenerateContentConfig(
				tools=[types.Tool(google_search=types.GoogleSearch())],
				system_instruction="근거 없는 수치나 사실을 확정하지 말고 출처와 불확실성을 명시하세요.",
			),
		)
		return DeepResearchResult(
			text=response.text or "Research 결과를 생성하지 못했습니다.",
			sources=self._extract_sources(response),
		)

	@staticmethod
	def _extract_sources(response: Any) -> list[ResearchSourceResult]:
		sources: list[ResearchSourceResult] = []
		candidates = getattr(response, "candidates", None) or []
		for candidate in candidates:
			metadata = getattr(candidate, "grounding_metadata", None)
			for chunk in getattr(metadata, "grounding_chunks", None) or []:
				web = getattr(chunk, "web", None)
				url = getattr(web, "uri", None) or getattr(web, "url", None)
				title = getattr(web, "title", None)
				if url and title:
					sources.append(ResearchSourceResult(url=url, title=title))
		return sources
