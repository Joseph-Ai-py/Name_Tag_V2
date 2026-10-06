from typing import Any

from app.llm.schemas import LLMResponse


DOMAIN_PROMPTS: dict[str, str] = {
    "discover_brand_interview": "Legacy O 인터뷰의 핵심 질문을 생성합니다. 5~10개의 4지선다 질문과 질문 목적을 JSON으로 반환합니다.",
    "generate_brand_candidates": "Legacy O MVB 후보 생성입니다. 서로 다른 4개 후보에 brand_name, brand_name_en, name_meaning, slogan, story_summary, seed_color, seed_color_reason을 포함합니다.",
    "select_brand_candidate": "선택된 후보 조각을 조합해 하나의 BrandInfo를 만듭니다. name, meaning, slogan, story, color 선택을 검증합니다.",
    "generate_brand_philosophy": "Legacy A1 결과를 생성합니다. brand_philosophy, brand_essence, core_identity를 중첩 구조로 반환합니다.",
    "generate_brand_story": "Legacy A2 결과를 생성합니다. naming_expansion, slogan_expansion, brand_story_full을 반환합니다.",
    "generate_positioning": "Legacy A3 결과를 생성합니다. positioning과 unbreakable_brand_promise를 반환합니다.",
    "generate_persona": "Legacy B1 결과를 생성합니다. 핵심 타겟, primary_persona, secondary_personas, emotional_triggers를 반환합니다.",
    "generate_customer_journey": "Legacy B2 결과를 생성합니다. 인지부터 재구매까지의 고객 여정과 채널별 행동을 반환합니다.",
    "analyze_customer_swot": "Legacy B4 결과를 생성합니다. strengths, weaknesses, opportunities, threats와 brand_responses를 반환합니다.",
    "generate_business_model": "Legacy B5 결과를 생성합니다. 문제, 가치 제안, 수익, 비용, 채널, 검증 가설을 반환합니다.",
    "generate_visual_identity": "Legacy C1 결과를 생성합니다. color_palette, typography, visual_mood_guide, design_principles를 반환합니다.",
    "generate_logo_identity": "Legacy DE logo identity 결과를 생성합니다. concept와 guide를 반환합니다.",
    "generate_character_guide": "Legacy DE character guide 결과를 생성합니다. intro, reasoning, story를 반환합니다.",
    "regenerate_brand_field": "Legacy O/A/B/C/DE 필드 재생성입니다. 지정 필드에 대한 정확히 3개의 후보를 반환합니다.",
}


def build_domain_prompt(skill_name: str, message: str, context: dict[str, Any]) -> str:
    instruction = DOMAIN_PROMPTS[skill_name]
    return (
        f"{instruction}\n"
        "사용자에게 의미 있는 근거만 제시하고 내부 사고과정은 출력하지 마세요.\n"
        f"요청: {message}\n"
        f"V2 context: {context}"
    )


def normalize_domain_response(skill_name: str, response: LLMResponse) -> LLMResponse:
    if skill_name not in DOMAIN_PROMPTS or response.proposed_changes:
        return response

    content = response.artifact_content or {"response": response.text}
    changes: dict[str, Any] | None = None
    if skill_name == "generate_positioning":
        changes = {"brand.positioning": content.get("positioning", content)}
    elif skill_name == "generate_brand_philosophy":
        identity = content.get("core_identity", {})
        changes = {
            "brand.mission": identity.get("mission"),
            "brand.vision": identity.get("vision"),
            "brand.values": identity.get("core_values", []),
        }
    elif skill_name == "generate_brand_story":
        changes = {"brand.story": content.get("brand_story_full", content)}
    elif skill_name == "generate_persona":
        changes = {"customer.persona": content.get("primary_persona", content)}
    elif skill_name == "generate_customer_journey":
        changes = {"customer.journey": content}
    elif skill_name == "analyze_customer_swot":
        changes = {"market.swot": content}
    elif skill_name == "generate_business_model":
        changes = {"business.business_model": content}
    elif skill_name == "generate_visual_identity":
        changes = {
            "visual.colors": content.get("color_palette", []),
            "visual.typography": content.get("typography"),
            "visual.mood": content.get("visual_mood_guide", content),
        }
    elif skill_name == "generate_logo_identity":
        changes = {"visual.logo": content}
    elif skill_name == "generate_character_guide":
        changes = {"visual.character": content}

    return LLMResponse(
        text=response.text,
        artifact_type=response.artifact_type,
        artifact_content=content,
        proposed_changes=changes,
    )