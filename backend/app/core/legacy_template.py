from copy import deepcopy
from typing import Any


_LEGACY_TEMPLATE: dict[str, Any] = {
    "brand_info": {
        "brand_name": "",
        "brand_name_en": "",
        "name_meaning": "",
        "slogan": "",
        "story_summary": "",
        "seed_color": "",
        "seed_color_reason": "",
    },
    "interview_data": {
        "interview_data_a": "",
        "interview_data_b": "",
        "interview_data_c": "",
        "interview_data_de": "",
    },
    "data_a": {
        "brand_philosophy": {
            "manifesto": "",
            "raison_detre": "",
            "stand_against": ["", "", ""],
            "stand_for": ["", "", ""],
        },
        "brand_essence": {
            "keyword": "",
            "keyword_explanation": "",
            "brand_definition": "",
        },
        "core_identity": {
            "mission": "",
            "vision": "",
            "core_values": [
                {"value": "", "description": "", "example": ""},
                {"value": "", "description": "", "example": ""},
                {"value": "", "description": "", "example": ""},
            ],
        },
        "naming_expansion": {
            "name_story": "",
            "domain_suggestions": ["", "", ""],
            "sns_handles": ["", "", ""],
            "alternative_names": [
                {"name": "", "name_en": "", "rationale": ""},
                {"name": "", "name_en": "", "rationale": ""},
            ],
        },
        "slogan_expansion": {
            "main_slogan_en": "",
            "sub_slogans": [
                {"slogan": "", "emphasis": ""},
                {"slogan": "", "emphasis": ""},
                {"slogan": "", "emphasis": ""},
            ],
        },
        "brand_story_full": "",
        "positioning": {
            "statement": "",
            "differentiators": [
                {"point": "", "description": ""},
                {"point": "", "description": ""},
                {"point": "", "description": ""},
            ],
            "positioning_map_visualized": {
                "axis_x": "",
                "axis_y": "",
                "quadrants_description": "",
                "our_exact_position": "",
            },
        },
        "unbreakable_brand_promise": {
            "declaration": "",
            "proof_of_promise": [
                {"channel": "", "actionable_rule": ""},
                {"channel": "", "actionable_rule": ""},
                {"channel": "", "actionable_rule": ""},
            ],
        },
    },
    "data_b": {
        "persona_strategy": {
            "strategic_reasoning": "",
            "core_target_group": {
                "definition": "",
                "demographics": "",
                "lifestyle_keywords": ["", "", "", "", ""],
                "consumption_behavior": "",
            },
            "primary_persona": {
                "name": "",
                "age_and_job": "",
                "daily_scene": "",
                "pain_point_and_desire": "",
                "emotional_needs": ["", "", ""],
                "deal_breaker": "",
            },
            "secondary_personas": [
                {"id": 1, "name_and_demographic": "", "character_type": "", "why_they_buy": ""},
                {"id": 2, "name_and_demographic": "", "character_type": "", "why_they_buy": ""},
                {"id": 3, "name_and_demographic": "", "character_type": "", "why_they_buy": ""},
                {"id": 4, "name_and_demographic": "", "character_type": "", "why_they_buy": ""},
            ],
            "emotional_triggers": [
                {"trigger": "", "reason": ""},
                {"trigger": "", "reason": ""},
                {"trigger": "", "reason": ""},
            ],
        },
        "customer_journey": {
            "strategic_reasoning": "",
            "customer_journey_map": [
                {"stage": "인지", "touchpoint": "", "customer_emotion": "", "brand_action": ""},
                {"stage": "탐색", "touchpoint": "", "customer_emotion": "", "brand_action": ""},
                {"stage": "구매", "touchpoint": "", "customer_emotion": "", "brand_action": ""},
                {"stage": "재구매", "touchpoint": "", "customer_emotion": "", "brand_action": ""},
                {"stage": "전파", "touchpoint": "", "customer_emotion": "", "brand_action": ""},
            ],
        },
    },
    "data_c": {
        "color_palette": [
            {"color_name": "", "hex_code": "#000000", "role": "Primary", "reason": ""},
            {"color_name": "", "hex_code": "#000000", "role": "Secondary", "reason": ""},
            {"color_name": "", "hex_code": "#000000", "role": "Accent", "reason": ""},
            {"color_name": "", "hex_code": "#FFFFFF", "role": "Background", "reason": ""},
            {"color_name": "", "hex_code": "#000000", "role": "Text Color", "reason": ""},
        ],
        "typography": {
            "primary_font": {"font_name_kr": "", "google_fonts_family": "", "weight_recommendation": 800, "usage_and_reason": ""},
            "secondary_font": {"font_name_kr": "", "google_fonts_family": "", "weight_recommendation": 400, "usage_and_reason": ""},
        },
        "visual_mood_guide": {
            "photography_do": ["", "", ""],
            "photography_dont": ["", "", ""],
            "mood_keywords": ["", "", "", "", ""],
        },
        "design_principles": {"layout_direction": "", "image_processing": ""},
    },
    "data_de": {
        "logo_identity": {
            "concept": {"symbol_reason": "", "color_reason": "", "overall_message": "", "direction_text": ""},
            "guide": {"minimum_size": "", "clear_space": ""},
        },
        "character_guide": {
            "intro": {"name": "", "appearance": "", "symbolic_value": ""},
            "reasoning": {"selection_reason": "", "emotional_connection": ""},
            "story": {"background": "", "brand_role": ""},
        },
        "logo_path": None,
        "char_path": None,
    },
}


def legacy_state_template() -> dict[str, Any]:
    """Return a fresh Legacy A-to-DE compatibility structure."""
    return deepcopy(_LEGACY_TEMPLATE)


def canonical_section_extensions() -> dict[str, dict[str, Any]]:
    """Return Legacy fields placed inside the existing V2 sections."""
    template = legacy_state_template()
    brand_info = template["brand_info"]
    data_a = template["data_a"]
    data_b = template["data_b"]
    data_c = template["data_c"]
    data_de = template["data_de"]
    return {
        "brand": {
            "name_en": brand_info["brand_name_en"],
            "name_meaning": brand_info["name_meaning"],
            "seed_color": brand_info["seed_color"],
            "seed_color_reason": brand_info["seed_color_reason"],
            "interview_data": template["interview_data"],
            "brand_philosophy": data_a["brand_philosophy"],
            "brand_essence": data_a["brand_essence"],
            "value_details": data_a["core_identity"]["core_values"],
            "naming_expansion": data_a["naming_expansion"],
            "slogan_expansion": data_a["slogan_expansion"],
            "positioning_detail": {
                "differentiators": data_a["positioning"]["differentiators"],
                "positioning_map_visualized": data_a["positioning"]["positioning_map_visualized"],
            },
            "unbreakable_brand_promise": data_a["unbreakable_brand_promise"],
        },
        "customer": {
            "persona_strategy": data_b["persona_strategy"],
            "journey_detail": data_b["customer_journey"],
        },
        "visual": {
            "visual_mood_guide": data_c["visual_mood_guide"],
            "design_principles": data_c["design_principles"],
            "logo_path": data_de["logo_path"],
            "char_path": data_de["char_path"],
        },
    }
