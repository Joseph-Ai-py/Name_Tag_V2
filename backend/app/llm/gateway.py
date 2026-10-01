from functools import lru_cache
from typing import Any, Protocol

from app.config import get_settings
from app.llm.schemas import LLMResponse


class LLMGateway(Protocol):
	def generate_text(
		self,
		task: str,
		message: str,
		context: dict[str, Any],
	) -> LLMResponse:
		...


class MockLLMGateway:
	responses = {
		"research": (
			"시장과 경쟁사 정보를 조사할 준비를 했어요. 먼저 조사 범위를 정해볼게요.",
			"market_research",
			"research_plan",
		),
		"customer": (
			"고객과 타겟을 정리할 준비를 했어요. 현재 고객 가설을 구체화해볼게요.",
			"customer_analysis",
			"define_customer",
		),
		"brand": (
			"브랜드 전략 결과를 만들 준비를 했어요. 핵심 메시지와 포지셔닝을 정리해볼게요.",
			"brand_strategy",
			"define_positioning",
		),
		"business": (
			"사업 구조를 정리할 준비를 했어요. 문제와 해결책의 관계를 확인해볼게요.",
			"business_discovery",
			"define_problem_solution",
		),
		"visual": (
			"비주얼 방향을 정리할 준비를 했어요. 브랜드 성격과 시각 요소를 연결해볼게요.",
			"visual_direction",
			"define_visual_direction",
		),
	}

	def generate_text(self, task: str, message: str, context: dict[str, Any]) -> LLMResponse:
		response = self.responses.get(task)
		if response is None:
			return LLMResponse(
				text="좋아요. 현재 브랜드 맥락을 유지하면서 다음 작업을 함께 정리해볼게요.",
			)

		text, artifact_type, next_step = response
		return LLMResponse(
			text=text,
			artifact_type=artifact_type,
			artifact_content={"request": message, "next_step": next_step},
		)


@lru_cache
def get_llm_gateway() -> LLMGateway:
	settings = get_settings()
	if settings.llm_provider == "gemini":
		from app.llm.gemini import GeminiGateway

		return GeminiGateway(
			api_key=settings.gemini_api_key,
			model=settings.gemini_model,
		)
	return MockLLMGateway()
