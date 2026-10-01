# NAME TAG V2

## Backend First 개발 계획서

### 1. 개발 원칙

NAME TAG V2는 다음 순서로 개발한다.

```text
Backend Function
↓
API Endpoint
↓
DB 저장/조회 검증
↓
Swagger에서 직접 테스트
↓
Integration Test
↓
Backend 완료
↓
Frontend 연결
```

핵심 원칙은 하나다.

> **프론트엔드에서 기능을 만들어서 백엔드를 검증하지 않는다.
> 백엔드 자체를 먼저 완성하고 API만으로 모든 핵심 기능을 검증한다.**

따라서 V2 개발 초기에는 프론트엔드 개발을 최소화하고 `backend/`를 독립적으로 사용할 수 있는 상태를 만드는 것을 최우선으로 한다.

---

# 2. 최종 Backend 목표

백엔드는 최종적으로 다음 구조를 갖는다.

```text
                    ┌──────────────────┐
                    │   API Router     │
                    │ auth / brands    │
                    │ chat / research  │
                    │ assets / export  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │    Services      │
                    │ User             │
                    │ Brand            │
                    │ Chat             │
                    │ Research         │
                    │ Asset            │
                    │ Export           │
                    └────────┬─────────┘
                             │
             ┌───────────────┼────────────────┐
             │               │                │
      ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
      │  Database   │ │    Agent   │ │   Storage   │
      │ SQLAlchemy  │ │ Router     │ │ Files       │
      │ Alembic     │ │ Context    │ │ Images      │
      │ BrandState  │ │ Skills     │ │ Documents   │
      │ Conversation│ │ Tools      │ │              │
      └─────────────┘ └─────┬──────┘ └─────────────┘
                             │
                    ┌────────▼─────────┐
                    │   LLM Service    │
                    │ Gemini           │
                    └──────────────────┘
```

---

# 3. 개발 완료의 기준

단순히 함수가 만들어졌다고 완료 처리하지 않는다.

각 기능은 아래 5단계를 모두 통과해야 한다.

### Level 1 — Function

Python 함수가 정상적으로 동작한다.

### Level 2 — API

FastAPI endpoint를 통해 호출할 수 있다.

### Level 3 — Persistence

필요한 데이터가 DB에 저장되고 다시 조회된다.

### Level 4 — Manual Test

Swagger UI(`/docs`)에서 실제 요청을 보내 직접 확인한다.

### Level 5 — Automated Test

pytest로 주요 성공/실패 케이스가 자동 검증된다.

즉,

```text
함수 구현
   ↓
API 연결
   ↓
DB 확인
   ↓
Swagger 수동 테스트
   ↓
pytest
   ↓
완료
```

---

# 4. 전체 개발 순서

## Phase 0. Backend 개발 환경 고정

### 목표

프론트 없이 backend만 실행할 수 있는 환경을 만든다.

### 확인 대상

```text
backend/
├── app.py
├── main.py
├── db.py
├── dependencies.py
├── models.py
├── schemas.py
├── routers/
├── services/
├── agent/
├── skills/
├── tools/
└── migrations/
```

### 구현

* FastAPI 앱 실행
* 환경변수 로딩
* DB 연결
* Alembic 연결
* CORS
* `/health`
* Swagger `/docs`
* Swagger `/openapi.json`

### 직접 테스트

```text
GET /health
```

성공 기준:

```json
{
  "status": "ok"
}
```

### 완료 조건

* 서버 정상 실행
* DB 연결 성공
* migration 성공
* `/docs` 정상 표시
* `/health` 성공

---

# 5. Phase 1 — Database 완성

현재 V2에서 DB와 Alembic 구조는 이미 있기 때문에 이것을 먼저 실제 동작 수준까지 완성한다.

## 목표

NAME TAG의 모든 핵심 데이터가 DB에 안전하게 저장될 수 있어야 한다.

### 핵심 Entity

```text
User
Brand
BrandState
Conversation
Message
ResearchJob
ResearchReport
Artifact
Asset
```

필요에 따라 이후 추가한다.

---

## 5-1. User

필드 예시:

```text
id
email
password_hash
name
created_at
updated_at
```

---

## 5-2. Brand

```text
id
user_id
name
description
created_at
updated_at
```

---

## 5-3. BrandState

Brand의 실제 사업/브랜드 상태를 저장한다.

```json
{
  "business": {},
  "market": {},
  "customer": {},
  "brand": {},
  "visual": {},
  "assets": [],
  "research": [],
  "feedback": [],
  "decisions": []
}
```

핵심 원칙:

> **BrandState를 NAME TAG의 Single Source of Truth로 사용한다.**

---

## 5-4. Conversation

```text
id
brand_id
user_id
title
created_at
updated_at
```

---

## 5-5. Message

```text
id
conversation_id
role
content
artifact
created_at
```

---

## 직접 테스트

DB에 직접 값을 넣고 조회해서 다음이 성립하는지 확인한다.

```text
User
 ↓
Brand
 ↓
BrandState
 ↓
Conversation
 ↓
Message
```

---

# 6. Phase 2 — Authentication / User API

## 목표

프론트 없이도 사용자 계정을 만들고 인증할 수 있어야 한다.

### API

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Register

요청:

```json
{
  "email": "test@example.com",
  "password": "password123",
  "name": "Joseph"
}
```

응답:

```json
{
  "id": "...",
  "email": "test@example.com",
  "name": "Joseph"
}
```

---

### Login

요청:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

응답:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

### Me

```text
GET /auth/me
Authorization: Bearer <TOKEN>
```

---

## 반드시 테스트할 실패 케이스

```text
이미 존재하는 이메일
잘못된 비밀번호
존재하지 않는 계정
토큰 없음
잘못된 토큰
만료된 토큰
```

### 완료 기준

Swagger에서

```text
Register
→ Login
→ Authorize
→ Me
```

순서로 실제 테스트 가능해야 한다.

---

# 7. Phase 3 — Brand CRUD

## 목표

사용자가 AI 작업을 시작할 Brand를 만들고 관리할 수 있게 한다.

### API

```text
POST   /brands
GET    /brands
GET    /brands/{brand_id}
PATCH  /brands/{brand_id}
DELETE /brands/{brand_id}
```

---

### 생성

```json
{
  "name": "NAME TAG",
  "description": "AI Brand Workspace"
}
```

---

### 테스트

```text
1. Brand 생성
2. Brand ID 확인
3. 전체 Brand 조회
4. 특정 Brand 조회
5. 이름 변경
6. 삭제
7. 삭제된 Brand 조회 → 404
```

### 중요한 검증

User A가 만든 Brand를 User B가 조회할 수 없어야 한다.

즉:

```text
Authorization
+
Ownership Check
```

를 반드시 구현한다.

---

# 8. Phase 4 — BrandState API

이 단계가 NAME TAG의 핵심이다.

## 목표

프론트가 없어도 BrandState를 생성/조회/수정할 수 있어야 한다.

### API

```text
GET   /brands/{brand_id}/state
PATCH /brands/{brand_id}/state
```

필요하면 특정 section 단위 API도 추가한다.

```text
PATCH /brands/{brand_id}/state/business
PATCH /brands/{brand_id}/state/customer
PATCH /brands/{brand_id}/state/brand
...
```

다만 초기에는 전체 BrandState PATCH 하나로 시작하는 것을 권장한다.

---

## BrandState 예시

```json
{
  "business": {
    "industry": "AI",
    "service": "AI Brand Workspace",
    "problem": "브랜드 기획 과정이 복잡하다",
    "solution": "AI가 브랜드 기획을 도와준다"
  },
  "market": {
    "tam": {},
    "sam": {},
    "som": {},
    "competitors": [],
    "swot": {},
    "business_model": {}
  },
  "customer": {
    "target": "",
    "segments": [],
    "persona": {},
    "needs": [],
    "pain_points": [],
    "journey": [],
    "jtbd": []
  },
  "brand": {
    "name": "",
    "mission": "",
    "vision": "",
    "values": [],
    "positioning": "",
    "story": "",
    "personality": [],
    "tone": "",
    "key_message": ""
  }
}
```

---

## 매우 중요한 테스트

### Test A — Save

```text
PATCH
 ↓
DB 저장
```

### Test B — Reload

```text
GET
 ↓
방금 저장한 데이터 확인
```

### Test C — 부분 수정

Business만 수정했을 때 다른 section이 사라지면 안 된다.

### Test D — 동시 수정 대비

향후 version 번호나 updated_at 기반 optimistic locking을 고려한다.

---

# 9. Phase 5 — Conversation API

## 목표

AI Consultant의 대화 데이터를 서버에서 관리한다.

### API

```text
POST /brands/{brand_id}/conversations
GET  /brands/{brand_id}/conversations
GET  /conversations/{conversation_id}
POST /conversations/{conversation_id}/messages
GET  /conversations/{conversation_id}/messages
```

---

## 테스트

```text
Brand 생성
 ↓
Conversation 생성
 ↓
Message 추가
 ↓
Message 조회
 ↓
새로고침
 ↓
동일 데이터 확인
```

---

# 10. Phase 6 — LLM Service

여기서부터 실제 AI가 들어간다.

현재 V2 구조의 `llm_service.py`를 중심으로 정리한다.

## 목표

LLM 호출 자체를 Router에서 직접 하지 않는다.

잘못된 구조:

```text
Router
 → Gemini
```

올바른 구조:

```text
Router
 → Service
 → Agent
 → LLM Service
 → Gemini
```

---

## LLM Service 책임

```text
generate_text()
generate_structured()
generate_image()
```

등으로 역할을 분리한다.

예:

```python
async def generate_text(...)
async def generate_structured(...)
async def generate_image(...)
```

---

## 직접 테스트 API

개발 환경에서만 사용할 수 있는 테스트 endpoint를 한시적으로 둔다.

예:

```text
POST /dev/llm/test
```

요청:

```json
{
  "prompt": "브랜드 전략이 무엇인지 한 문장으로 설명해줘"
}
```

응답:

```json
{
  "text": "..."
}
```

이 endpoint는 Production에서는 비활성화한다.

---

# 11. Phase 7 — Skill System

이제 Agent가 사용할 실제 기능을 만든다.

현재 구조:

```text
skills/
├── base.py
├── registry.py
├── discovery.py
├── business.py
├── market.py
├── customer.py
├── brand_strategy.py
├── visual_direction.py
└── creative_asset.py
```

여기서 중요한 것은 **파일을 만들어놓는 것이 아니라 각 Skill이 실제로 실행되는 것**이다.

---

## Skill 공통 인터페이스

예:

```python
class Skill:
    name: str

    async def execute(
        self,
        context,
        input_data
    ):
        ...
```

---

# 12. Skill 개발 순서

한 번에 전부 만들지 않는다.

### 1차

```text
Discovery
Brand Strategy
```

### 2차

```text
Business
Customer
Market
```

### 3차

```text
Visual Direction
Creative Asset
```

---

# 13. Skill별 테스트 구조

예를 들어 Brand Strategy Skill:

```text
입력
 ↓
BrandState
 ↓
Brand Strategy Skill
 ↓
Structured Output
 ↓
Artifact
```

예상 결과:

```json
{
  "mission": "...",
  "vision": "...",
  "values": [],
  "positioning": "...",
  "tone": "...",
  "key_message": "..."
}
```

---

# 14. 중요한 원칙 — Skill은 바로 DB를 수정하지 않는다

처음에는 다음 구조로 만든다.

```text
Skill
 ↓
Result
 ↓
Artifact
 ↓
User Approval
 ↓
BrandState Mutation
```

즉 AI가 마음대로 BrandState를 덮어쓰게 하지 않는다.

예:

```json
{
  "artifact_type": "brand_strategy",
  "content": {
    "positioning": "...",
    "mission": "...",
    "values": []
  },
  "proposed_changes": [
    "brand.positioning",
    "brand.mission",
    "brand.values"
  ]
}
```

이 구조가 나중에 Human-in-the-loop의 기반이 된다.

---

# 15. Phase 8 — Agent Core

이 단계에서 현재의

```text
agent/
├── context.py
├── llm.py
├── loop.py
├── router.py
├── tools.py
└── types.py
```

를 실제 작동하는 Agent로 만든다.

---

## Agent 흐름

```text
User Message
      ↓
Agent
      ↓
Context Manager
      ↓
Router
      ↓
Skill / Tool 선택
      ↓
Execution
      ↓
Result
      ↓
Artifact
      ↓
BrandState Update
      ↓
Conversation 저장
```

---

# 16. Agent Router

사용자 입력:

> "우리 브랜드의 타깃 고객을 정리해줘"

Agent가:

```text
customer
```

Skill을 선택한다.

사용자:

> "우리 시장 규모를 조사해줘"

↓

```text
market
+
research
```

사용자:

> "로고를 만들어줘"

↓

```text
visual
+
creative_asset
```

처럼 연결된다.

---

# 17. Agent 테스트

프론트 없이 API로 테스트한다.

```text
POST /chat
```

예:

```json
{
  "brand_id": "...",
  "conversation_id": "...",
  "message": "우리 브랜드의 타깃 고객을 정의해줘"
}
```

Agent가 실제로

```text
Router
→ Skill
→ LLM
→ Result
→ Conversation
```

전체를 통과하는지 확인한다.

---

# 18. Phase 9 — Tool System

현재 구조:

```text
tools/
├── base.py
├── registry.py
├── web_search.py
├── research.py
├── browser.py
├── document.py
├── image.py
└── export.py
```

이 부분도 파일 존재 여부가 아니라 실제 실행 여부를 기준으로 구현한다.

---

# 19. Tool 개발 순서

### 1차

```text
Web Search
```

### 2차

```text
Research
```

### 3차

```text
Document
```

### 4차

```text
Image
```

### 5차

```text
Export
```

---

# 20. Quick Research

먼저 Deep Research보다 Quick Research를 완성한다.

목표:

```text
사용자 요청
 ↓
Agent
 ↓
Research Tool
 ↓
검색
 ↓
Source 수집
 ↓
Structured Result
```

결과:

```json
{
  "query": "...",
  "summary": "...",
  "sources": [
    {
      "title": "...",
      "url": "...",
      "summary": "..."
    }
  ]
}
```

---

# 21. Research 데이터 모델

향후 Deep Research를 위해 처음부터 Research를 별도 객체로 관리한다.

```text
ResearchJob
ResearchReport
ResearchFinding
ResearchSource
```

상태:

```text
planning
approved
queued
running
normalizing
completed
failed
cancelled
```

---

# 22. Phase 10 — Deep Research

Deep Research는 가장 나중에 개발한다.

이유:

```text
DB
 ↓
BrandState
 ↓
Agent
 ↓
Tool
 ↓
Research
```

기반이 없으면 Deep Research를 만들어도 저장하고 활용할 곳이 없다.

---

## Deep Research 구조

```text
User Request
      ↓
Agent
      ↓
Research Plan
      ↓
사용자 승인
      ↓
Research Job
      ↓
Background Execution
      ↓
Raw Report
      ↓
Normalize
      ↓
ResearchReport
      ↓
Finding
      ↓
Source
      ↓
사용자 검토
      ↓
BrandState 반영
```

---

# 23. Phase 11 — Artifact System

AI가 생성하는 결과를 단순 문자열로 저장하지 않는다.

예:

```text
Artifact
```

를 중심으로 관리한다.

종류:

```text
brand_strategy
business_model
market_analysis
customer_persona
swot
research_report
visual_direction
document
image
```

---

## Artifact 구조

```json
{
  "id": "...",
  "type": "brand_strategy",
  "title": "Brand Strategy",
  "content": {},
  "status": "draft",
  "created_at": "...",
  "updated_at": "..."
}
```

상태:

```text
draft
approved
rejected
archived
```

---

# 24. Phase 12 — Asset / File Storage

이미지와 문서를 DB에 전부 넣지 않는다.

구조:

```text
Database
 └─ metadata

Storage
 └─ actual file
```

예:

```text
Asset
 ├─ id
 ├─ brand_id
 ├─ type
 ├─ filename
 ├─ mime_type
 ├─ storage_path
 └─ metadata
```

---

# 25. Phase 13 — Export

마지막에 Export를 붙인다.

처음부터 PDF를 중심으로 만들지 않는다.

내부적으로는:

```text
BrandState
+
Artifacts
+
Research
+
Assets
```

를 가지고 있고

마지막에

```text
Export
 ↓
PDF
DOCX
JSON
```

등으로 변환하는 구조로 만든다.

---

# 26. Backend API 최종 구조

최종적으로는 대략 다음과 같은 API가 된다.

```text
/auth
    POST /register
    POST /login
    GET  /me

/users
    GET /me
    PATCH /me

/brands
    POST /
    GET /
    GET /{brand_id}
    PATCH /{brand_id}
    DELETE /{brand_id}

/brands/{brand_id}/state
    GET /
    PATCH /

/brands/{brand_id}/conversations
    POST /
    GET /

/conversations
    GET /{conversation_id}
    DELETE /{conversation_id}

/conversations/{conversation_id}/messages
    POST /
    GET /

/chat
    POST /

/research
    POST /
    GET /{research_id}
    POST /{research_id}/approve
    POST /{research_id}/cancel

/artifacts
    GET /{artifact_id}
    PATCH /{artifact_id}
    POST /{artifact_id}/approve
    POST /{artifact_id}/reject

/assets
    POST /
    GET /
    DELETE /{asset_id}

/export
    POST /
    GET /{export_id}
```

실제 경로는 구현 과정에서 조정할 수 있지만, 기능 책임은 이 정도로 분리한다.

---

# 27. 수동 테스트 환경

Backend가 완성될 때까지 프론트엔드를 거의 사용하지 않는다.

주력 도구:

```text
FastAPI Swagger
    ↓
/docs
```

보조:

```text
curl
Postman
pytest
```

가 된다.

---

# 28. Swagger 테스트 시나리오

## Scenario 1 — 회원

```text
Register
 ↓
Login
 ↓
Authorize
 ↓
Me
```

## Scenario 2 — Brand

```text
Create Brand
 ↓
Get Brand
 ↓
Update Brand
 ↓
Get Brands
```

## Scenario 3 — BrandState

```text
Get State
 ↓
Update State
 ↓
Get State
 ↓
변경 확인
```

## Scenario 4 — Conversation

```text
Create Conversation
 ↓
Send Message
 ↓
Get Messages
```

## Scenario 5 — AI

```text
Chat
 ↓
Agent
 ↓
Skill
 ↓
LLM
 ↓
Artifact
 ↓
Conversation 저장
```

## Scenario 6 — Research

```text
Research 요청
 ↓
Job 생성
 ↓
실행
 ↓
Report 생성
 ↓
Source 확인
```

---

# 29. 자동 테스트 구조

Backend에는 처음부터 테스트 디렉터리를 만든다.

```text
backend/
└── tests/
    ├── conftest.py
    ├── test_health.py
    ├── test_auth.py
    ├── test_users.py
    ├── test_brands.py
    ├── test_brand_state.py
    ├── test_conversations.py
    ├── test_chat.py
    ├── test_agent.py
    ├── test_skills.py
    ├── test_tools.py
    ├── test_research.py
    └── test_export.py
```

---

# 30. 테스트의 세 단계

### Unit Test

개별 함수 검사.

```text
service
skill
router helper
parser
validator
```

### Integration Test

```text
API
 ↓
Service
 ↓
DB
```

### E2E Backend Test

```text
User
 ↓
Brand
 ↓
BrandState
 ↓
Conversation
 ↓
Agent
 ↓
Skill
 ↓
Artifact
 ↓
DB
```

---

# 31. 개발 완료 체크포인트

각 Phase는 아래 형식으로 완료 처리한다.

```text
[ ] 함수 구현
[ ] Schema 작성
[ ] Router 연결
[ ] DB 연동
[ ] 성공 케이스 테스트
[ ] 실패 케이스 테스트
[ ] Swagger 수동 테스트
[ ] pytest 테스트
[ ] 로그/에러 처리
[ ] 문서화
```

---

# 32. 실제 개발 순서

전체 순서는 다음과 같이 고정한다.

```text
STEP 01
Backend 실행 환경
        ↓
STEP 02
DB / Migration
        ↓
STEP 03
Auth / User
        ↓
STEP 04
Brand CRUD
        ↓
STEP 05
BrandState
        ↓
STEP 06
Conversation
        ↓
STEP 07
LLM Service
        ↓
STEP 08
Discovery Skill
        ↓
STEP 09
Brand Strategy Skill
        ↓
STEP 10
Agent
        ↓
STEP 11
Customer / Business / Market Skill
        ↓
STEP 12
Tool System
        ↓
STEP 13
Quick Research
        ↓
STEP 14
Artifact
        ↓
STEP 15
Asset
        ↓
STEP 16
Deep Research
        ↓
STEP 17
Export
        ↓
STEP 18
Backend 전체 Integration Test
        ↓
STEP 19
Frontend 연결
```

---

# 33. 가장 중요한 개발 규칙

## Rule 1

프론트에서 필요한 기능을 생각하고 백엔드를 만드는 것이 아니라,

```text
Backend Contract
→ API
→ Manual Test
→ Frontend
```

순서로 간다.

---

## Rule 2

`파일이 있다 = 구현 완료`로 판단하지 않는다.

예를 들어

```text
skills/market.py
```

가 존재해도 실제 실행되지 않는다면

```text
진행률 100%
```

이 아니라

```text
Skeleton
```

이다.

---

## Rule 3

모든 기능은 Swagger에서 테스트 가능해야 한다.

프론트가 없어도:

```text
회원가입
브랜드 생성
BrandState 수정
AI 요청
Research
Artifact 생성
```

까지 가능해야 한다.

---

## Rule 4

AI보다 데이터 구조를 먼저 안정화한다.

```text
DB
 ↓
BrandState
 ↓
Artifact
 ↓
Conversation
 ↓
Agent
```

이 구조가 안정된 후 AI 기능을 확장한다.

---

## Rule 5

Deep Research와 복잡한 Agent를 너무 빨리 만들지 않는다.

먼저:

```text
CRUD
+
Persistence
+
LLM
+
Skill
```

을 완성한다.

그 다음:

```text
Agent
+
Research
+
Deep Research
```

로 확장한다.

---

# 34. Backend 완성 판정 기준

아래 시나리오가 프론트 없이 모두 성공하면 Backend Phase를 종료한다.

```text
1. 회원가입
        ↓
2. 로그인
        ↓
3. Brand 생성
        ↓
4. BrandState 조회
        ↓
5. BrandState 수정
        ↓
6. Conversation 생성
        ↓
7. 메시지 전송
        ↓
8. Agent 실행
        ↓
9. Skill 실행
        ↓
10. LLM 응답
        ↓
11. Artifact 생성
        ↓
12. Artifact 저장
        ↓
13. Research 실행
        ↓
14. Research 결과 저장
        ↓
15. Asset 저장
        ↓
16. Export 생성
```

그리고 서버를 재시작한 뒤에도

```text
User
Brand
BrandState
Conversation
Artifact
Research
Asset
```

가 그대로 조회되어야 한다.

---

# 35. 이번 V2에서 당장 해야 할 것

현재 상태에서는 모든 기능을 한꺼번에 구현하지 않는다.

**첫 번째 목표는 다음 5개다.**

```text
① DB 정상 동작

② Auth 정상 동작

③ Brand CRUD 정상 동작

④ BrandState 저장/조회 정상 동작

⑤ Conversation 저장/조회 정상 동작
```

이 5개가 끝나면 Swagger만 가지고도 **“실제 NAME TAG Backend가 존재한다”**&#xACE0; 말할 수 있는 상태가 된다.

그 다음에야

```text
LLM
→ Skill
→ Agent
→ Research
```

를 올린다.

---

# 36. 최종 개발 철학

NAME TAG V2의 개발 단위를

```text
페이지
```

가 아니라

```text
Backend Capability
```

로 바꾼다.

예를 들어 기존 방식:

```text
Brand 페이지 만들기
Market 페이지 만들기
Customer 페이지 만들기
```

가 아니라,

```text
Brand CRUD
BrandState
Brand Strategy Skill
Customer Skill
Market Research
Artifact
```

를 먼저 만든다.

그렇게 하면 나중에 프론트가

```text
Desktop
Mobile
Chat
Workspace
```

등 어떤 형태가 되더라도 동일한 Backend를 사용할 수 있다.

**최종 목표는 “프론트가 없어도 NAME TAG의 핵심 기능을 API만으로 전부 실행할 수 있는 Backend”를 먼저 완성하는 것이다.**
