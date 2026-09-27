# NAME TAG Tool 설계

> 개정판: Multi-user / Authentication 반영


## 문서 목적

이 문서는 Agent가 사용할 수 있는 **실제 행동 단위(Tool)**를 정의한다.

핵심 원칙:

> Skill은 작업 방법을 정의하고, Tool은 실제 행동을 수행한다.

---

# 1. Skill과 Tool의 차이

사용자 요청:

> "우리 서비스의 경쟁사를 조사해줘."

```text
Agent
 ↓
Competitor Analysis Skill
 ↓
Search Web Tool
 ↓
Get Web Page Tool
 ↓
Extract Information Tool
 ↓
Save Research Tool
 ↓
Create Finding Tool
 ↓
Propose Brand Change Tool
```

## Skill

> **작업 방법과 실행 순서를 정의**

예:

```text
competitor-analysis

1. 경쟁사 후보를 찾는다.
2. 공식 정보를 우선 조사한다.
3. 가격/서비스/타겟을 추출한다.
4. 경쟁사 간 차이를 분석한다.
5. 결과를 Research에 저장한다.
6. 필요한 경우 전략적 Finding을 만든다.
7. Brand 변경이 필요하면 Proposal을 만든다.
```

## Tool

> **실제 행동**

```text
search_web()
get_web_page()
save_research()
create_finding()
propose_brand_change()
apply_brand_change()
```

---

# 2. NAME TAG Tool 전체 구조

```text
TOOLS
│
├── ① Identity / Access Tools
├── ② Brand Tools
├── ② Conversation Tools
├── ③ Research Tools
├── ④ Strategy Tools
├── ⑤ Creative Tools
└── ⑥ Workspace Tools
      ├── Document
      ├── Block
      ├── Asset
      └── Export
```

Tool의 역할은 Skill의 세부 실행을 가능하게 하는 것이다.

---


---

# 3. ① Identity / Access Tools

인증 자체는 AI Tool이 아니다. 회원가입/로그인/로그아웃은 일반 Backend API에서 처리한다. 다만 Agent가 현재 사용자와 Brand의 범위를 판단해야 하므로 최소한의 **identity context**를 제공한다.

## `get_current_user_context`

```python
get_current_user_context()
```

결과:

```json
{
  "user_id": "user_001",
  "email": "user@example.com",
  "brand_id": "brand_001",
  "role": "owner"
}
```

## `list_my_brands`

```python
list_my_brands()
```

현재 사용자가 접근 가능한 Brand 목록만 반환한다.

## `get_brand_members`

```python
get_brand_members(brand_id: str)
```

현재 사용자가 해당 Brand를 볼 권한이 있는 경우에만 반환한다.

### 중요한 규칙

Agent가 다음 값을 직접 만들어 Tool에 넣는 방식은 사용하지 않는다.

```text
user_id
owner_user_id
``

현재 사용자 정보는 인증 middleware가 주입하고 Tool executor가 최종 검증한다.

인증 API:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

이 API는 Agent Tool Registry에 등록하지 않는다.

# 3. ② Brand Tools

## `get_brand_state`

현재 브랜드 전체 상태를 가져온다.

```python
def get_brand_state(brand_id: str):
    ...
```

## `get_brand_context`

전체 BrandState가 아니라 현재 작업에 필요한 정보만 가져온다.

```python
def get_brand_context(brand_id: str, task: str):
    ...
```

예:

```text
logo_generation
→
brand.name
brand.positioning
brand.personality
visual.colors
visual.typography
visual.mood
```

Token 비용을 줄이는 핵심 Tool이다.

## `propose_brand_change`

BrandState 변경안을 만든다.

```python
def propose_brand_change(
    brand_id: str,
    path: str,
    value: object,
    reason: str,
    affected_paths: list[str]
):
    ...
```

예:

```text
customer.target
대학생 → 취업준비생
```

## `apply_brand_change`

승인된 Proposal만 실제 BrandState에 반영한다.

```python
def apply_brand_change(change_id: str):
    ...
```

실행 순서:

```text
Snapshot
 ↓
Mutation
 ↓
History
```

## `create_brand_snapshot`

변경 직전 상태를 저장한다.

## `get_brand_history`

과거 변경사항을 조회한다.

```python
def get_brand_history(
    brand_id: str,
    field: str | None = None
):
    ...
```

---


### Brand Tool 권한 규칙

모든 Brand Tool은 현재 인증된 사용자와 Brand membership을 검사한다.

```text
Authenticated User
 ↓
BrandMember
 ↓
Tool Permission
```

`brand_id`가 다른 사용자의 리소스를 가리키더라도 membership이 없으면 실행하지 않는다.

# 4. ③ Conversation Tools

## `get_conversation_context`

최근 대화와 요약을 가져온다.

```python
def get_conversation_context(
    brand_id: str,
    limit: int = 20
):
    ...
```

## `save_conversation_summary`

긴 대화를 압축한다.

```python
def save_conversation_summary(
    brand_id: str,
    summary: str,
    decisions: list
):
    ...
```

중요 결정은 Conversation Summary와 Decision에 기록할 수 있지만, 구조화된 브랜드 값 자체는 BrandState가 기준이다.

---

# 5. ④ Research Tools

Research Tool은 **조사 결과를 바로 BrandState에 쓰지 않는다.**

기본 흐름:

```text
Search
 ↓
Source
 ↓
Research Record
 ↓
Finding
 ↓
Proposal
 ↓
Approval
 ↓
BrandState
```

## `search_web`

```python
def search_web(query: str, limit: int = 5):
    ...
```

## `get_web_page`

```python
def get_web_page(url: str):
    ...
```

## `extract_research_data`

```python
def extract_research_data(
    content: str,
    fields: list[str]
):
    ...
```

## `save_research`

```python
def save_research(
    brand_id: str,
    title: str,
    source: str,
    url: str,
    finding: str,
    research_date: str
):
    ...
```

실제 서비스에서는 ResearchReport/Source/Findings 모델에 맞춘 구조화된 저장 형태로 발전시킨다.

## `get_research`

```python
def get_research(
    brand_id: str,
    query: str
):
    ...
```

## `refresh_research`

오래된 연구를 다시 조사한다.

```python
def refresh_research(research_id: str):
    ...
```

## Deep Research 전용 Tool

```text
create_research_job
get_research_job
approve_research_plan
start_research_job
cancel_research_job
get_research_report
get_research_sources
get_research_findings
apply_research_finding
```

---


### Research 사용자 범위

ResearchJob/Report/Source/Finding에는 최소한 다음 context가 연결된다.

```text
user_id
brand_id
created_by
```

Research API/Tool은 현재 사용자가 해당 Brand의 member인지 확인한 뒤 조회/생성한다.

`user_id`를 query parameter로 받아 다른 사용자의 Research를 조회하는 방식은 사용하지 않는다.

# 6. 시장조사 Skill과 Tool 조합

예를 들어 `competitor-analysis` Skill은 내부적으로 다음을 수행한다.

```text
search_web()
 ↓
get_web_page()
 ↓
extract_research_data()
 ↓
save_research()
 ↓
create_finding()
 ↓
propose_brand_change()
```

중요한 원칙:

> Agent가 모든 Tool을 직접 조합하지 않고 Skill이 전문 작업의 순서를 관리한다.

---

# 7. ⑤ Strategy Tools

AI 분석 작업을 실행한다.

## `analyze_customer`

```python
def analyze_customer(brand_id: str):
    ...
```

결과:

```text
Segment
Persona
Needs
Pain Points
JTBD
Customer Journey
```

## `generate_positioning`

```python
def generate_positioning(brand_id: str):
    ...
```

중요한 결과는 필요하면 Proposal 형태로 반환한다.

## `generate_swot`

```python
def generate_swot(brand_id: str):
    ...
```

## `generate_business_model`

```python
def generate_business_model(brand_id: str):
    ...
```

## `generate_market_analysis`

```python
def generate_market_analysis(brand_id: str):
    ...
```

Research가 필요한 경우 Strategy Tool이 직접 외부 검색을 하는 것이 아니라 Research Skill을 사용한다.

---

# 8. TAM / SAM / SOM

초기에는 하나의 분석 흐름으로 묶을 수 있다.

```python
def analyze_market_size(brand_id: str):
    ...
```

TAM/SAM/SOM은 반드시:

```text
Research
+
Source
+
Calculation / Assumption
```

을 함께 관리한다.

근거 없는 숫자를 BrandState에 사실처럼 저장하지 않는다.

---

# 9. ⑥ Creative Tools

## `generate_brand_name`

```python
def generate_brand_name(
    brand_id: str,
    count: int = 10
):
    ...
```

## `generate_brand_story`

```python
def generate_brand_story(brand_id: str):
    ...
```

## `generate_tagline`

```python
def generate_tagline(brand_id: str):
    ...
```

## `generate_tone_of_voice`

```python
def generate_tone_of_voice(brand_id: str):
    ...
```

---

# 10. Visual Tools

## `generate_visual_direction`

```python
def generate_visual_direction(brand_id: str):
    ...
```

결과:

```text
Color
Typography
Mood
Photography
Graphic Style
Design Principles
```

## `generate_logo`

```python
def generate_logo(
    brand_id: str,
    direction: str | None = None
):
    ...
```

## `generate_character`

```python
def generate_character(
    brand_id: str,
    direction: str | None = None
):
    ...
```

## `generate_brand_image`

```python
def generate_brand_image(
    brand_id: str,
    prompt: str
):
    ...
```

이미지 Tool은 생성 후 Asset Record를 함께 만든다.

---

# 11. ⑦ Workspace Tools

Workspace는 제품 차별화의 핵심이다.

## `create_document`

```python
def create_document(
    brand_id: str,
    title: str
):
    ...
```

## `get_document`

```python
def get_document(document_id: str):
    ...
```

## `update_document`

```python
def update_document(
    document_id: str,
    changes: object
):
    ...
```

## `create_block`

```python
def create_block(
    document_id: str,
    type: str,
    content: object
):
    ...
```

## `update_block`

```python
def update_block(
    block_id: str,
    content: object
):
    ...
```

AI 편집의 핵심 Tool이다.

## `delete_block`

```python
def delete_block(block_id: str):
    ...
```

중요 문서는 자동 삭제를 제한하거나 사용자 확인을 요구할 수 있다.

## `move_block`

```python
def move_block(
    block_id: str,
    target_position: int
):
    ...
```

---

# 12. Asset Tools

## `get_assets`

```python
def get_assets(
    brand_id: str,
    asset_type: str | None = None
):
    ...
```

## `save_asset`

```python
def save_asset(
    brand_id: str,
    type: str,
    url: str,
    metadata: object
):
    ...
```

## `update_asset`

```python
def update_asset(
    asset_id: str,
    changes: object
):
    ...
```

## `delete_asset`

```python
def delete_asset(asset_id: str):
    ...
```

삭제는 Agent가 무조건 자동 실행하기보다 사용자 확인을 우선한다.

---

# 13. Export Tools

## `export_pdf`

```python
def export_pdf(
    brand_id: str,
    document_id: str
):
    ...
```

## `export_brand_kit`

```python
def export_brand_kit(brand_id: str):
    ...
```

예:

```text
brand-kit.zip
├── logo/
├── character/
├── colors/
├── typography/
├── brand-guide.pdf
└── brand-summary.pdf
```

---

# 14. Tool Permission

Agent에게 모든 Tool을 무제한으로 제공하지 않는다.

## READ

조회만 수행한다.

```text
get_brand_state
get_brand_context
get_conversation_context
get_research
get_research_report
get_document
get_assets
get_brand_history
```

## WRITE

새로운 결과/제안/문서를 만든다.

```text
save_conversation_summary
save_research
create_document
create_block
save_asset
create_research_job
propose_brand_change
```

## ACTION

외부 상태나 중요한 상태를 변경한다.

```text
apply_brand_change
approve_research_plan
apply_research_finding
start_research_job
refresh_research
cancel_research
export_pdf
```

ACTION Tool은 필요 시 사용자 승인을 요구한다.

---


---

# 15-A. 내부 서비스: Usage / Audit

사용량 기록과 보안 감사 로그는 LLM Tool이 아니라 Backend 내부 서비스로 둔다.

## UsageEvent

```text
record_usage_event(
  user_id,
  brand_id,
  feature,
  model,
  request_id,
  metrics
)
```

예:

```text
feature = deep_research
feature = image_generation
feature = chat
feature = export
```

## AuditLog

```text
record_audit_event(
  actor_user_id,
  brand_id,
  action,
  resource_type,
  resource_id
)
```

AI에게 `record_usage_event`나 `record_audit_event`를 선택하게 하지 않는다. 시스템이 작업 결과를 기준으로 자동 기록한다.

# 15. 최종 Tool 목록

## V1에서 실제 구현할 Tool

### Brand

```text
get_brand_state
get_brand_context
propose_brand_change
apply_brand_change
create_brand_snapshot
get_brand_history
```

### Conversation

```text
get_conversation_context
save_conversation_summary
```

### Research

```text
search_web
get_web_page
extract_research_data
save_research
get_research
refresh_research
```

### Strategy

```text
analyze_customer
generate_positioning
generate_swot
generate_business_model
generate_market_analysis
```

### Creative

```text
generate_brand_name
generate_brand_story
generate_tagline
generate_tone_of_voice
generate_visual_direction
generate_logo
generate_character
generate_brand_image
```

### Workspace

```text
create_document
get_document
update_document
create_block
update_block
delete_block
move_block
get_assets
save_asset
update_asset
delete_asset
export_pdf
```

Deep Research Tool은 Research Engine 구현 단계에서 추가한다.

---

# 16. 실제 Agent에는 모든 Tool을 전부 노출하지 않는다

Agent는 현재 작업에 필요한 Tool subset만 사용한다.

예:

```text
사용자:
"로고를 만들어줘"

Agent Context
 ↓
brand.name
brand.positioning
brand.personality
visual.colors
visual.typography
visual.mood

Allowed Tools
 ↓
get_brand_context
generate_logo
save_asset
propose_brand_change
```

Research Tool이나 금융/외부 서비스 등 무관한 Tool은 노출하지 않는다.

---

# 17. 핵심 관계

```text
Agent
 ↓
Router
 ↓
Skill
 ↓
Tool
 ↓
Artifact / Proposal
 ↓
Approval
 ↓
BrandState / Workspace
```

Research는 다음 흐름을 따른다.

```text
Research Tool
 ↓
Research Report
 ↓
Finding
 ↓
Brand Change Proposal
 ↓
User Approval
 ↓
BrandState
```

**Research Tool이 `update_brand_state()`를 직접 호출하는 구조는 사용하지 않는다.**

---

# 18. Tool 설계 원칙

1. Tool은 한 가지 행동에 집중한다.
2. Tool 입력/출력은 명확한 schema를 가진다.
3. READ/WRITE/ACTION 권한을 구분한다.
4. 외부 부작용이 있는 Tool은 idempotency 또는 confirmation을 고려한다.
5. 중요한 Mutation은 History와 연결한다.
6. Skill이 작업 순서를 담당하고 Tool은 개별 행동을 담당한다.
7. Tool Registry와 Agent prompt를 분리한다.
8. Tool 수가 늘어나면 Context에 맞게 subset을 선택한다.


## Multi-user 보안 규칙

1. 모든 보호 Tool은 authenticated request context를 가진다.
2. `user_id`는 LLM 입력이 아니라 세션에서 결정한다.
3. `brand_id`는 URL/request에 있더라도 membership을 반드시 재검증한다.
4. READ/WRITE/ACTION 권한은 Brand role과 Tool permission을 모두 통과해야 한다.
5. ACTION은 사용자 승인 또는 명시적 사용자 요청이 필요한 경우가 있다.
6. Usage/Audit은 모델이 선택하는 Tool이 아니라 시스템 서비스가 기록한다.
7. 다른 사용자의 존재 여부까지 노출하지 않도록 권한 실패 메시지는 최소화한다.
