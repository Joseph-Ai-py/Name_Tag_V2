# Legacy to V2 Skill Migration

기준 Legacy repository: `Joseph-Ai-py/Name_Tag`, HEAD `5a537a31af15250b09e69689d9c5a66eccfab00c`

이 문서는 Legacy 저장소를 실제 코드 기준으로 조사한 결과와 NAME TAG V2 Skill Registry로의 이식 상태를 기록한다. O/A/B/C/DE의 실행 순서는 V2 Agent의 고정 pipeline으로 복제하지 않는다.

## Legacy Inventory

| Legacy 영역 | 실제 파일 | 확인된 Prompt / Schema | 실제 기능 | V2 상태 |
| --- | --- | --- | --- | --- |
| O | `streamlit/logic_o.py`, `backend/routers/section_o.py` | `get_O_interview_prompt`, `get_O_mvb_prompt`, `InterviewResponseSchema`, `CandidatesResponse` | 인터뷰 질문, 4개 MVB 후보, 사용자 선택 조합, 필드 재생성 | PARTIALLY_MIGRATED |
| A | `streamlit/logic_a.py`, `backend/routers/section_a.py` | `get_A1_philosophy_prompt`, `get_A2_story_prompt`, `get_A3_positioning_prompt`, `A1ResponseSchema`, `A2ResponseSchema`, `A3ResponseSchema` | 철학/에센스/코어 아이덴티티, 스토리/네이밍 확장, 포지셔닝/브랜드 약속, 필드 재생성 | PARTIALLY_MIGRATED |
| B | `streamlit/logic_b.py`, `backend/routers/section_b.py` | `get_B1_persona_prompt`, `get_B2_journey_prompt`, `get_B4_customer_swot_prompt`, `get_B5_business_model_prompt`, `CustomerSWOTResponseSchema`, `BusinessModelResponseSchema` | Persona, Customer Journey, Customer SWOT, Business Model, 필드 재생성 | PARTIALLY_MIGRATED |
| C | `streamlit/logic_c.py`, `backend/routers/section_c.py` | `get_C0_visual_interview_prompt`, `get_C1_visual_identity_prompt`, `CResponseSchema` | Color Palette, Typography, Visual Mood Guide, Design Principles, 필드 재생성 | PARTIALLY_MIGRATED |
| DE | `streamlit/logic_de.py`, `backend/routers/section_de.py`, `backend/services/image_service.py` | `get_DE_interview_prompt`, `get_DE_identity_prompt`, `DEResponseSchema` | Logo Identity, Character Guide, logo/character 이미지 생성, 단독 재생성 | PARTIALLY_MIGRATED |

## V2 Skill Mapping

### O: Discovery

- `discover_brand_interview`
- `generate_brand_candidates`
- `select_brand_candidate`
- `regenerate_brand_field`

Legacy O의 `apply_candidate_mix`가 요구하는 `name`, `meaning`, `slogan`, `story`, `color` 선택 개념을 보존한다. 후보 조합은 BrandState 변경이므로 Proposal을 거쳐야 한다.

### A: Brand Strategy

- `generate_brand_philosophy`
- `generate_brand_story`
- `generate_positioning`
- `regenerate_brand_field`

A1의 `brand_philosophy`, `brand_essence`, `core_identity`와 A2/A3의 중첩 구조를 artifact로 보존하고, V2 state에는 다음 경로를 사용한다.

- `brand.mission`
- `brand.vision`
- `brand.values`
- `brand.story`
- `brand.positioning`

### B: Customer / Business

- `generate_persona` -> `customer.persona`
- `generate_customer_journey` -> `customer.journey`
- `analyze_customer_swot` -> `market.swot`
- `generate_business_model` -> `business.business_model`

B의 실제 함수는 A 결과와 인터뷰 답변을 context로 합쳐 B1/B2/B4/B5를 실행한다. V2에서는 이 결합을 Agent context와 skill dependencies로 표현하며 B 전체를 하나의 고정 단계로 실행하지 않는다.

### C: Visual

- `generate_visual_identity`
- `regenerate_brand_field`

Legacy CResponse의 `color_palette`, `typography`, `visual_mood_guide`, `design_principles`를 artifact로 보존하고 다음 state 경로에 매핑한다.

- `visual.colors`
- `visual.typography`
- `visual.mood`

`visual.design_principles` 전용 BrandState 경로는 현재 V2 초기 state에 없으므로 artifact로 우선 보존한다.

### DE: Creative / Asset

- `generate_logo_identity` -> `visual.logo`
- `generate_character_guide` -> `visual.character`
- Legacy 이미지 생성 호출은 `backend/services/image_service.py`에서 확인했다.

V2에는 아직 Legacy Gemini image provider와 파일 저장 adapter가 없으므로 `generate_logo_image`, `generate_character_image` Tool은 NOT_MIGRATED로 분류한다. V2의 기존 `save_asset` Tool과 연결하는 작업은 다음 단계에서 provider adapter를 추가한 뒤 진행해야 한다. 이미지 생성 placeholder를 완료 기능으로 표시하지 않는다.

## Dependency Graph

```text
Discovery / O
  -> brand.name, brand.story, customer.target

Brand / A
  -> brand.mission, brand.vision, brand.values, brand.positioning

Customer / Business / B
  -> customer.persona, customer.journey, market.swot, business.business_model

Visual / C
  -> visual.colors, visual.typography, visual.mood

Creative / DE
  -> visual.logo, visual.character
```

주요 dependency metadata는 V2 `SkillDefinition`에 저장한다.

- `generate_positioning`: `customer.target`, `market.competitors`
- `generate_customer_journey`: `customer.persona`
- `generate_business_model`: `customer.persona`
- `generate_logo_identity`: `brand.positioning`, `visual.colors`

## Skill Architecture

V2 registry는 Legacy section 이름을 `run_o`, `run_a`처럼 등록하지 않는다. 각 domain capability를 독립 Skill로 등록하고 다음 metadata를 가진다.

- description / purpose
- required_context / optional_context
- output_paths / dependencies
- artifact_type
- risk_level
- proposal_required

`SkillExecutor`는 기존 `LLMGateway`를 재사용하면서 domain prompt adapter를 적용하고, `normalize_domain_response`가 Legacy 형태를 V2 BrandState-compatible Proposal changes로 변환한다. Agent가 필요할 때만 이 Skill들을 선택한다.

## Regeneration

Legacy O/A/B/C/DE의 `re-generate` endpoint와 `normalize_candidates` 흐름을 확인했다. V2에는 `regenerate_brand_field` metadata를 등록했으며, 사용자 선택값과 현재 BrandState는 context로 전달되어야 한다. 실제 field별 후보 prompt의 provider 실행과 UI 재선택 workflow는 PARTIALLY_MIGRATED다.

## Status

### MIGRATED

- Legacy O/A/B/C/DE 기능 inventory
- Prompt / Schema inventory
- 주요 domain Skill registry
- Skill dependency metadata
- Legacy positioning output의 `brand.positioning` mapping
- proposal-required metadata
- domain skill parity tests

### PARTIALLY_MIGRATED

- Legacy prompt의 핵심 목적과 output shape를 V2 domain prompt adapter에 반영
- O candidate selection
- A/B/C/DE 전체 structured output의 provider-level validation
- field-level regeneration
- Artifact와 Proposal의 실제 domain별 생성

### NOT_MIGRATED

- Legacy Gemini 이미지 생성 provider
- `generate_logo_image`, `generate_character_image`와 V2 Object Storage/Asset 연결
- Legacy PDF builder의 모든 출력 layout
- 사용자 응답을 기다렸다가 중단된 Interview를 resume하는 human interaction workflow

### Intentionally Not Copied

- O -> A -> B -> C -> DE 고정 실행 pipeline
- Legacy router별 독립 DB 상태
- Legacy 이미지 파일 경로를 V2 BrandState에 직접 저장하는 방식

## Tests

- `tests/test_domain_skills.py`: Legacy-derived Skill registration, dependency metadata, output normalization
- `tests/test_skill_registry.py`: 기존 SkillExecutor compatibility

LLM 문장 일치 여부가 아니라 registry 계약, required context, output path, Proposal 경계와 schema-compatible mapping을 검증한다.
