# NAME TAG — Frontend Architecture & UX Specification

> 현재 `Joseph-Ai-py/Name_Tag` GitHub 저장소의 실제 프론트엔드 구조와 AI Brand Workspace 방향을 기반으로 한 Frontend 아키텍처 및 UX 기술 명세.
>
> 핵심 원칙: **Chat은 입력 방식이고, Workspace가 제품이다.**
>
> 추가 원칙: **사용자는 로그인된 계정의 소유 범위 안에서 Brand를 만들고, 각 Brand의 모든 상태·대화·Research·Asset을 독립적으로 관리한다.**

---

# 1. 문서 목적

현재 NAME TAG의 프론트엔드는 브랜드 제작 과정을:

```text
Section O
→ Section A
→ Section B
→ Section C
→ Section DE
→ Preview
```

형태로 보여준다.

기능 자체는 이미 상당 부분 구현되어 있지만 UX 관점에서는 사용자가 AI 브랜드 제작 서비스의 내부 프로세스를 그대로 따라가야 한다.

앞으로는 이 구조를:

```text
Authentication
        ↓
Brand Selection / Creation
        ↓
AI Consultant
        ↓
Agent
        ↓
Skill / Tool
        ↓
BrandState
        ↓
Workspace
```

형태로 바꾼다.

단, 기존 Section 기능을 버리지 않고 내부 기능으로 재사용한다.

로그인을 추가하면서 NAME TAG의 프론트엔드는 단일 세션형 화면이 아니라 다음 구조를 갖는다.

```text
User
  ↓
Brand
  ↓
Workspace
  ├── BrandState
  ├── Conversation
  ├── Research
  ├── Documents
  ├── Assets
  └── History
```

---

# 2. 현재 GitHub 프론트엔드 분석

현재 저장소에는 다음 기술이 사용되고 있다.

```text
React
TypeScript
Vite
React Router
Zustand
TanStack Query
Axios
Tailwind CSS
Vitest
Playwright
```

`frontend/package.json` 기준으로 이미 Zustand와 TanStack Query가 함께 구성되어 있으므로 새로운 상태관리 라이브러리를 추가할 필요가 없다.

현재 프론트엔드는 `brandStore.ts`에 Section별 상태가 많이 모여 있으므로 향후에는:

```text
Server State
→ TanStack Query

UI State
→ Zustand
```

형태로 분리한다.

---

# 3. 현재 라우팅

현재 핵심 Router는:

```text
/
/generate
```

형태이며 `Generate.tsx`에서:

```text
currentStep === 0 → SectionO
currentStep === 1 → SectionA
currentStep === 2 → SectionB
currentStep === 3 → SectionC
currentStep === 4 → SectionDE
currentStep === 5 → Preview
```

로 렌더링한다.

향후에는 로그인 여부와 Brand 선택 여부까지 Routing에 포함한다.

---

# 4. 현재 상태 구조

현재 `brandStore.ts`에서는 다음과 같은 상태가 중심이다.

```text
brandData

interviewDataO
brandInfo

interviewDataA
dataA

interviewDataB
dataB

interviewDataC
dataC

interviewDataDE
dataDE

currentStep
isLoading
error
```

또한 interview snapshot과 applied selections 같은 보조 상태도 존재한다.

향후에는 이를 모두 즉시 삭제하지 않고 migration adapter를 통해 새로운 구조로 연결한다.

```text
Legacy Store
    ↓
Legacy → BrandState Adapter
    ↓
Server BrandState
```

---

# 5. 현재 프론트엔드의 장점

현재 코드를 전부 버리고 새로 만들 필요는 없다.

이미 다음 요소가 존재한다.

### 생성 기능

* SectionO
* SectionA
* SectionB
* SectionC
* SectionDE

### 결과 표시

* Preview
* Result Displays
* PdfPreviewSidebar

### 편집

* PdfVariableSidebar
* RightSidebar

### 상태관리

* brandStore

### 테스트

* Vitest
* Playwright scaffold

따라서 새로운 Frontend는 기존 기능을 **recomposition**하는 방식으로 구현해야 한다.

---

# 6. 현재 문제

## 문제 1. 내부 프로세스가 UI가 됨

사용자는 브랜드를 만들고 싶은데:

```text
O
A
B
C
DE
```

라는 제작 시스템을 이해해야 한다.

---

## 문제 2. 선형 흐름

현재:

```text
O
↓
A
↓
B
↓
C
↓
DE
```

하지만 실제 브랜드 제작은:

```text
Target 변경
→ Positioning 변경
→ Tone 변경
→ Visual 변경
```

처럼 앞뒤로 움직인다.

---

## 문제 3. 사용자와 데이터의 경계가 없음

기존 구조에서는 브라우저 상태를 중심으로 브랜드 데이터를 관리했다.

로그인 이후에는:

```text
User A
  └── Brand A

User B
  └── Brand B
```

가 명확하게 분리되어야 한다.

따라서 Frontend는 항상 현재 인증된 User와 현재 선택된 Brand를 알고 있어야 한다.

---

# 7. 목표 UX

사용자가 느끼는 것은:

```text
Login
  ↓
My Brands
  ↓
AI Consultant
```

이어야 한다.

Workspace에 들어간 이후에는:

```text
AI Consultant
```

가 핵심 인터페이스다.

내부적으로는:

```text
Discovery
Strategy
Market
Customer
Visual
Creative
```

가 실행된다.

---

# 8. 전체 사용자 흐름

전체 Frontend UX는 다음을 기준으로 한다.

```text
Landing
   ↓
Login / Sign Up
   ↓
Authentication
   ↓
Brand Dashboard
   ↓
Create Brand / Select Brand
   ↓
Workspace
   ↕
AI Consultant
   ↕
Research / Edit / Generate
   ↓
Workspace
```

기존 HTML 프로토타입은:

```text
Login
→ Workspace
```

전환을 구현하고 있다.

실제 제품에서는 중간에 Brand Dashboard / Brand Selector가 추가된다.

---

# 9. 인증 화면

로그인 화면은 현재 HTML 프로토타입의 방향을 유지한다.

현재 시안:

```text
┌────────────────────────────────┐
│                                │
│          NAME TAG              │
│                                │
│      AI Brand Workspace        │
│                                │
│ 이메일                         │
│ [ name@example.com ]           │
│                                │
│ 비밀번호                       │
│ [ •••••••• ]                  │
│                                │
│ □ 로그인 유지   비밀번호 찾기 │
│                                │
│ [ 로그인 ]                     │
│                                │
│ 계정이 없으신가요?             │
│ 무료로 회원가입                │
│                                │
└────────────────────────────────┘
```

인증 화면에서도 Theme Toggle을 제공한다.

현재 HTML처럼 로그인 화면에서는 우측 상단에 Floating Theme Button을 둘 수 있다.

---

# 10. Authentication 화면 종류

최소 다음 화면을 지원한다.

```text
/login
/signup
/forgot-password
/reset-password
```

향후 필요하면:

```text
/verify-email
```

을 추가한다.

---

# 11. 로그인 UX

사용자가:

```text
Email
Password
```

를 입력한다.

Frontend:

```text
POST /api/auth/login
```

을 호출한다.

성공:

```text
Session 생성
↓
Current User 조회
↓
Brand Dashboard
```

실패:

```text
Invalid email or password
```

등의 사용자 친화적인 오류를 표시한다.

인증 토큰 자체를 일반 화면 상태나 localStorage에 저장하는 것을 기본 방식으로 사용하지 않는다.

Session은 Backend에서 관리하고 Frontend는 인증 상태를 조회한다.

---

# 12. 로그인 유지

HTML 프로토타입의:

```text
□ 로그인 유지
```

옵션은 실제 구현에서는 Session 정책으로 연결한다.

권장 UX:

```text
Unchecked
→ 세션 유지 기간을 짧게

Checked
→ 장기 세션
```

다만 실제 Session 만료와 Refresh 전략은 Backend 인증 정책을 따른다.

Frontend는 Session의 내부 토큰 값을 직접 다루지 않는다.

---

# 13. 로그아웃

Workspace Sidebar 하단에:

```text
Logout
```

을 제공한다.

사용자가 로그아웃하면:

```text
POST /api/auth/logout
↓
Server Session 종료
↓
Query Cache 정리
↓
Login 화면
```

으로 이동한다.

사용자별 데이터가 다음 사용자에게 노출되지 않도록 이전 User의 Query Cache를 반드시 제거한다.

---

# 14. 현재 사용자 정보

로그인 이후 Frontend는 현재 사용자를 다음 형태로 관리한다.

```typescript
type User = {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  createdAt: string;
};
```

Frontend에서 필요한 최소 정보만 관리한다.

비밀번호나 인증 secret은 Frontend State에 저장하지 않는다.

---

# 15. Authentication State

Authentication State는 서버 상태를 기준으로 한다.

```typescript
type AuthUserState = {
  user: User | null;
  authenticated: boolean;
  loading: boolean;
};
```

예:

```text
useQuery(["auth", "me"])
```

또는 이에 준하는 `authApi.me()`를 사용한다.

---

# 16. Protected Route

Workspace는 로그인되지 않은 사용자가 접근할 수 없다.

```text
/landing
   ↓
/login
   ↓
/brands
   ↓
/workspace/:brandId
```

Protected Route:

```tsx
<RequireAuth>
  <Workspace />
</RequireAuth>
```

인증되지 않은 경우:

```text
→ /login
```

으로 이동한다.

---

# 17. Brand Dashboard

로그인 후 바로 특정 Brand Workspace를 여는 대신 기본적으로 Brand Dashboard를 제공한다.

```text
My Brands

[ + 새 Brand 만들기 ]

┌──────────────┐
│ MY BRAND     │
│ Dessert      │
│ Updated 2h   │
│ [열기]       │
└──────────────┘

┌──────────────┐
│ TRAVEL AI    │
│ Travel       │
│ Updated 1d   │
│ [열기]       │
└──────────────┘
```

사용자는 한 계정에서 여러 Brand를 관리할 수 있다.

---

# 18. Brand 생성

로그인 후:

```text
[+ 새 Brand]
```

를 누르면 초기 Conversation을 시작할 수 있다.

예:

```text
무엇을 만들고 있나요?

[ 사업 아이디어를 자유롭게 입력하세요 ]

예:
"대학생들이 부담 없이 사용할 수 있는
AI 기반 여행 계획 서비스를 만들고 있어."
```

생성 후:

```text
Brand 생성
↓
Brand ID 발급
↓
BrandState 초기화
↓
Conversation 생성
↓
Workspace
```

---

# 19. Brand Context

Workspace에 들어가면 현재 Brand를 항상 표시한다.

HTML 프로토타입의:

```text
CURRENT BRAND

M
MY BRAND
▼
```

구조를 유지한다.

다만 실제 제품에서는 클릭 시 Brand Switcher를 제공한다.

```text
CURRENT BRAND

MY BRAND
────────────

Travel AI
Food Brand
Portfolio

[+ New Brand]
[Manage Brands]
```

---

# 20. Brand Ownership

모든 Workspace 데이터는 현재 Brand를 기준으로 접근한다.

개념적으로:

```text
User
 ↓
Brand
 ↓
BrandState
Conversation
Research
Documents
Assets
History
```

Frontend는 모든 Brand API 요청에 `brandId`를 포함한다.

---

# 21. Brand 권한

향후 협업을 고려하여 Brand의 Member 개념을 사용한다.

```text
BrandMember

owner
editor
viewer
```

Frontend는 권한에 따라 Action UI를 제어한다.

예:

```text
owner
→ 모든 변경 가능

editor
→ 편집 가능

viewer
→ 읽기 전용
```

Frontend에서 버튼을 숨기는 것만으로 보안을 완성하지 않는다.

실제 권한 검사는 Backend가 수행한다.

---

# 22. 제품 화면 정의

NAME TAG의 메인 UI는 세 부분으로 구성한다.

```text
┌─────────────────────────────────────────────────────┐
│                 Application Header                  │
├──────────────┬────────────────────────┬─────────────┤
│              │                        │             │
│ Navigation   │     Main Workspace     │ AI          │
│              │                        │ Consultant  │
│ Overview     │     Content            │ Chat        │
│ Business     │     Document           │ Artifact    │
│ Market       │     Research           │ Suggestions │
│ Customer     │     Editor             │ Progress    │
│ Brand        │                        │             │
│ Visual       │                        │             │
│ Assets       │                        │             │
│ Research     │                        │             │
│ History      │                        │             │
└──────────────┴────────────────────────┴─────────────┘
```

---

# 23. Layout

## Desktop

```text
Navigation: 220~240px
Main: flexible
AI Consultant: 360~420px
```

예:

```text
240px + 1fr + 400px
```

중앙 영역은 최대 너비를 제한하지 않고 문서/Research에 따라 유동적으로 사용한다.

---

# 24. Header

Header에는 최소한 다음을 둔다.

```text
NAME TAG
[Brand Name]

Saved
Research
Export
Settings
```

추가 사용자 영역:

```text
[Avatar] User Name ▼
```

Dropdown:

```text
Account
Settings
Usage
Logout
```

---

# 25. Header 상태

```text
Saving...
Saved
Unsaved changes
Research running
```

Research가 실행 중이면 Header에서 상태를 표시할 수 있다.

예:

```text
● Research running
```

---

# 26. Workspace Navigation

사용자에게 O/A/B/C/DE는 보여주지 않는다.

다음 구조를 사용한다.

```text
Overview
Business
Market
Customer
Brand
Visual
Assets
Research
History
```

---

# 27. Overview

Overview는 브랜드 전체 상태를 빠르게 보는 Dashboard다.

표시:

```text
Brand Name
One-line Description
Target
Positioning
Brand Values
Current Stage
Recent Research
Recent Changes
Incomplete Items
```

예:

```text
MY BRAND

"20대를 위한 경험형 디저트 브랜드"

Target
20대 대학생 / 직장인

Positioning
...

Recent Research
한국 디저트 시장 조사
2시간 전

Needs Attention
○ 경쟁사 조사 부족
○ 가격 전략 미완성
```

---

# 28. Business

Business는 브랜드가 아니라 사업의 구조를 보여준다.

```text
Problem
Solution
Product / Service
Business Model
Revenue Model
Pricing
Distribution
Stage
```

각 항목은 editable artifact로 표시한다.

---

# 29. Market

Market은 Deep Research와 가장 밀접하게 연결된다.

```text
Market Overview

TAM
SAM
SOM

Growth
Trends
Competitors
Pricing
Opportunities
SWOT
```

중요한 숫자와 문장에는 source indicator를 붙인다.

```text
TAM
₩XX조 [3 sources]
```

---

# 30. Customer

```text
Target
Segments
Persona
Needs
Pain Points
Journey
JTBD
```

Target을 변경하면 AI가 영향 범위를 알려준다.

예:

```text
Target 변경

영향 가능성이 있는 항목:

High
- Persona
- Customer Journey
- Positioning

Medium
- Brand Message
- Tone

Low
- Visual Direction
```

---

# 31. Brand

```text
Name
Mission
Vision
Values
Philosophy
Positioning
Personality
Story
Tone
Key Message
Tagline
```

각 항목을 독립적인 Artifact로 관리한다.

---

# 32. Visual

```text
Color
Typography
Mood
Logo
Character
Photography
Graphic Style
Design Principles
```

이미지 Asset은 별도 Asset Gallery와 연결한다.

---

# 33. Assets

```text
Logos
Characters
Brand Images
Documents
Exports
```

Asset마다:

```text
type
version
created_at
source
prompt
related_brand_state
```

를 저장할 수 있도록 한다.

---

# 34. Research

Research는 일반 문서가 아니라 별도의 작업 공간이다.

```text
Research

[New Research]

Running
  한국 디저트 시장 분석
  진행 중

Recent Reports
  경쟁사 분석
  고객 트렌드
  가격 조사

Sources
Findings
```

---

# 35. History

History는 단순한 페이지 수정 이력이 아니다.

```text
User Edit
AI Edit
Research Applied
Brand Decision
Regeneration
Snapshot
```

을 모두 관리한다.

예:

```text
09/27 13:20

Target 변경

Before
20대 여성

After
20대 대학생

Changed by
User

Impact
Persona
Positioning
Customer Journey
```

---

# 36. AI Consultant

AI Consultant는 오른쪽 고정 Panel로 제공한다.

```text
┌────────────────────────────┐
│ AI Consultant              │
├────────────────────────────┤
│                            │
│ AI                         │
│ 현재 브랜드를 보면...       │
│                            │
│ [Artifact Card]            │
│                            │
│ User                       │
│ 좀 더 전문적으로 해줘       │
│                            │
│ AI                         │
│ 수정된 버전을 만들었어요.   │
│                            │
├────────────────────────────┤
│ 무엇을 할까요?          ↑  │
└────────────────────────────┘
```

---

# 37. AI Consultant의 역할

Consultant는 단순 대화 모델이 아니다.

다음을 수행한다.

```text
질문
계획
Research
생성
수정
비교
적용
검증
```

---

# 38. Message Type

Frontend에서는 메시지 종류를 타입으로 정의한다.

```typescript
type MessageType =
  | "message"
  | "question"
  | "suggestion"
  | "artifact"
  | "research_plan"
  | "research_progress"
  | "research_result"
  | "confirmation"
  | "change_summary";
```

---

# 39. Artifact Message

AI가 결과를 생성하면 일반 텍스트 대신 Artifact를 보여준다.

```text
┌──────────────────────────────┐
│ Positioning                 │
│                              │
│ 20대 1인 가구를 위한...      │
│                              │
│ [적용] [수정] [재생성]       │
└──────────────────────────────┘
```

---

# 40. Artifact의 의미

Artifact는 단순 메시지가 아니라 Workspace의 특정 객체와 연결된다.

```json
{
  "artifact_id": "artifact_001",
  "type": "positioning",
  "target": "brand.positioning",
  "content": "...",
  "status": "proposed"
}
```

---

# 41. Artifact Lifecycle

```text
generated
   ↓
proposed
   ↓
approved
   ↓
applied
```

또는:

```text
proposed
   ↓
rejected
```

---

# 42. 자연어 수정

사용자가:

```text
"좀 더 고급스럽게 바꿔줘."
```

라고 입력한다.

Frontend는 현재 선택된 Artifact Context를 함께 보낸다.

```json
{
  "message": "좀 더 고급스럽게 바꿔줘.",
  "context": {
    "artifact_id": "artifact_001",
    "target": "brand.positioning"
  }
}
```

---

# 43. AI Edit 흐름

```text
User Message
    ↓
Current Artifact
    ↓
Brand Context
    ↓
Agent
    ↓
Generate Alternative
    ↓
Artifact
    ↓
User Approval
    ↓
BrandState
```

---

# 44. 첫 진입 화면

기존 Home에서 바로 SectionO로 넘어가는 대신:

```text
무엇을 만들고 있나요?

[ 사업 아이디어를 자유롭게 입력하세요 ]

예:

"대학생들이 부담 없이 사용할 수 있는
AI 기반 여행 계획 서비스를 만들고 있어."
```

를 제공한다.

---

# 45. 초기 Conversation

AI:

```text
좋아요.

현재 이해한 내용을 정리하면:

사업
AI 여행 계획 서비스

문제
여행 계획을 세우는 데 시간이 오래 걸림

타겟
대학생

제가 몇 가지 질문을 하면서
사업과 브랜드의 방향을 잡아볼게요.
```

이후 질문:

```text
가장 해결하고 싶은 문제는 무엇인가요?
```

---

# 46. Workspace 생성 시점

BrandState가 일정 수준 이상 채워지면 Workspace를 활성화한다.

예:

```text
business.service
business.problem
business.target
```

등 최소 핵심 정보가 확보된 시점.

그 이전에는 Conversation 중심 UI.

---

# 47. Progressive Workspace

처음부터 빈 페이지를 전부 보여주지 않는다.

```text
Initial

Chat only
    ↓
BrandState 생성
    ↓
Workspace 생성
    ↓
Sections progressively available
```

이 방식은 빈 화면에 대한 부담을 줄인다.

---

# 48. Research UI

AI Consultant에서:

```text
"시장 조사를 해줘."
```

라고 하면 Research UI로 전환한다.

---

# 49. Research Plan Card

```text
┌────────────────────────────────────┐
│ Deep Research                     │
│                                    │
│ 한국 디저트 시장 진입 가능성       │
│                                    │
│ 조사 범위                         │
│ ✓ Market                          │
│ ✓ Customer                        │
│ ✓ Competitor                      │
│ ✓ Pricing                         │
│                                    │
│ [계획 수정] [조사 시작]            │
└────────────────────────────────────┘
```

---

# 50. Research Progress

```text
Researching...

✓ Planning
✓ Market Data
✓ Competitors
● Consumer Trends
○ Analysis
○ Report

27 sources
```

프론트에서 내부 Thought를 노출하는 대신 사용자에게 의미 있는 진행 상태만 보여준다.

---

# 51. Research Report UI

Main Workspace에서 Report를 연다.

```text
┌──────────────────────────────────────────────┐
│ 한국 디저트 시장 분석                         │
│                                              │
│ Executive Summary                            │
│                                              │
│ Market                                       │
│ ─────────                                    │
│ ...                                          │
│                                              │
│ Competitors                                  │
│                                              │
│ | Brand | Price | Target |                   │
│                                              │
│ Findings                                     │
│                                              │
│ [Finding Card]                               │
└──────────────────────────────────────────────┘
```

---

# 52. Source UI

Source는 우측 Drawer 또는 Report 내부에서 확인한다.

```text
Sources

[1] 한국농수산식품유통공사
    Official
    Published: 2026-XX-XX

[2] 기업 공식 자료
    Company

[3] Research Report
```

---

# 53. Finding UI

```text
Finding

20대 소비자의 경험 중심 소비 증가

Evidence

[1] [2] [4]

AI 제안

Customer Needs에 반영

[적용] [저장] [닫기]
```

---

# 54. Frontend State Architecture

현재:

```text
brandInfo
dataA
dataB
dataC
dataDE
currentStep
```

에서 다음으로 이동한다.

```text
App State

├── Auth State
├── UI State
├── Brand State
├── Conversation State
└── Research State
```

단, 이 중 Server State는 TanStack Query가 관리한다.

---

# 55. Auth State

인증 상태의 Source of Truth는 서버다.

```typescript
type AuthState = {
  user: User | null;
  authenticated: boolean;
  loading: boolean;
};
```

Front-end는 다음 값을 자체 추측하지 않는다.

```text
authenticated = true
```

를 브라우저 localStorage만으로 관리하지 않는다.

Session 확인 결과를 기준으로 한다.

---

# 56. UI State

Zustand가 담당한다.

```typescript
type UIState = {
  sidebarOpen: boolean;
  consultantOpen: boolean;
  activePanel: string;
  theme: "light" | "dark";
  mobileDrawer: string | null;
  selectedArtifactId: string | null;
  selectedBlockId: string | null;
};
```

UI state는 서버에 저장하지 않는다.

---

# 57. Brand State

서버가 Source of Truth다.

```typescript
type BrandState = {
  business: BusinessState;
  market: MarketState;
  customer: CustomerState;
  brand: BrandIdentityState;
  visual: VisualState;
  assets: Asset[];
};
```

Frontend에서 임의로 전체 BrandState를 소유하지 않는다.

---

# 58. Conversation State

```typescript
type ConversationState = {
  conversationId: string;
  messages: Message[];
  summary: string;
};
```

대화 자체는 서버에 저장한다.

Frontend에는 현재 화면 표시를 위한 cache를 둔다.

---

# 59. Research State

```typescript
type ResearchState = {
  jobs: ResearchJob[];
  activeJobId?: string;
  reports: ResearchReport[];
};
```

Research Job은 현재 User와 현재 Brand에 귀속된 데이터만 조회한다.

---

# 60. TanStack Query 역할

TanStack Query는 다음을 관리한다.

```text
Current User
Brands
Brand State
Brand Documents
Research Jobs
Research Reports
Assets
Conversation
History
```

---

# 61. Query Key와 사용자 경계

Query Key는 최소한 리소스 단위가 명확해야 한다.

예:

```typescript
["auth", "me"]

["brands"]

["brand", brandId]

["brand", brandId, "state"]

["research", brandId]

["research-job", jobId]

["research-report", reportId]

["document", documentId]

["assets", brandId]
```

Frontend는 임의의 `userId`를 Query Key에 넣어서 보안을 구현하지 않는다.

실제 권한과 데이터 소유권은 Backend가 검증한다.

---

# 62. Zustand 역할

Zustand는 다음만 관리한다.

```text
sidebar
drawer
active panel
theme
modal
selected artifact
selected block
temporary editor state
```

다음은 Zustand에 저장하지 않는다.

```text
Password
Session Token
전체 BrandState
전체 Conversation
Research database
```

---

# 63. API Layer

현재 Axios 기반 구조를 유지한다.

파일:

```text
src/api/
```

목표:

```text
src/api/

├── client.ts
├── auth.ts
├── users.ts
├── brands.ts
├── agent.ts
├── research.ts
├── documents.ts
└── assets.ts
```

`client.ts`는 인증된 Session 기반 요청을 공통 처리한다.

---

# 64. API 인증 원칙

Frontend는 일반적으로:

```text
API Request
  ↓
Session Cookie
  ↓
Backend
  ↓
Current User
  ↓
Brand Permission
  ↓
Resource Access
```

흐름을 따른다.

Frontend에서 다음처럼 User ID를 직접 넣어서 소유권을 결정하지 않는다.

```text
POST /api/brand

{
  "user_id": "..."
}
```

대신 Backend가 현재 인증된 세션에서 User를 결정한다.

---

# 65. API 예시

Authentication:

```text
POST /api/auth/login
POST /api/auth/signup
POST /api/auth/logout
GET  /api/auth/me
POST /api/auth/forgot-password
```

Brand:

```text
GET  /api/brands
POST /api/brands
GET  /api/brands/:brandId
PATCH /api/brands/:brandId
```

Workspace:

```text
GET /api/brand/:brandId/state
```

Research:

```text
POST /api/research/quick
POST /api/research/jobs
GET  /api/research/jobs/:id
GET  /api/research/reports/:id
```

---

# 66. Route Architecture

현재:

```text
/
/generate
```

목표:

```text
/
/login
/signup
/forgot-password
/brands

/workspace/:brandId
/workspace/:brandId/overview
/workspace/:brandId/business
/workspace/:brandId/market
/workspace/:brandId/customer
/workspace/:brandId/brand
/workspace/:brandId/visual
/workspace/:brandId/assets
/workspace/:brandId/research
/workspace/:brandId/history
```

---

# 67. Route Protection

다음 페이지는 인증이 필요하다.

```text
/brands
/workspace/*
```

다음 페이지는 인증이 없어도 접근 가능하다.

```text
/
/login
/signup
/forgot-password
```

Workspace route에는 추가로 Brand Membership 검증이 필요하다.

---

# 68. Route의 원칙

URL은 현재 사용자가 보고 있는 Workspace 위치를 표현한다.

예:

```text
/workspace/brand_001/market
```

이렇게 하면 새로고침해도 같은 위치를 유지할 수 있다.

현재 `currentStep` 기반 navigation보다 훨씬 적합하다.

---

# 69. WorkspaceLayout

```tsx
<WorkspaceLayout>

  <WorkspaceSidebar />

  <WorkspaceMain>
    <WorkspaceHeader />
    <WorkspaceContent />
  </WorkspaceMain>

  <ConsultantPanel />

</WorkspaceLayout>
```

---

# 70. Layout 구조

```text
src/

├── layouts/
│   └── WorkspaceLayout.tsx
```

책임:

* 전체 grid
* responsive
* navigation
* consultant 영역
* global actions

---

# 71. Authentication Layout

```text
src/layouts/

├── AuthLayout.tsx
└── WorkspaceLayout.tsx
```

AuthLayout:

```text
Theme
Logo
Auth Card
Background
```

WorkspaceLayout:

```text
Sidebar
Header
Main
Consultant
```

로 역할을 분리한다.

---

# 72. Workspace Sidebar

```text
src/features/workspace/components/WorkspaceSidebar.tsx
```

책임:

* 메뉴 표시
* active section
* collapse
* mobile drawer
* current brand
* brand switcher
* user menu

---

# 73. Main Workspace

```text
src/features/workspace/components/WorkspaceContent.tsx
```

Route에 따라 현재 화면을 렌더링한다.

---

# 74. Feature 구조

기능별로 폴더를 나눈다.

```text
src/features/

├── auth/
├── brands/
├── workspace/
├── consultant/
├── research/
├── business/
├── market/
├── customer/
├── brand/
├── visual/
├── assets/
├── editor/
└── history/
```

---

# 75. Auth Feature

```text
auth/

├── components/
│   ├── LoginForm.tsx
│   ├── SignupForm.tsx
│   ├── ForgotPasswordForm.tsx
│   ├── AuthCard.tsx
│   └── AuthError.tsx
├── hooks/
│   ├── useCurrentUser.ts
│   └── useAuth.ts
├── api.ts
├── types.ts
└── guards/
    └── RequireAuth.tsx
```

---

# 76. Brand Feature

```text
brands/

├── components/
│   ├── BrandCard.tsx
│   ├── BrandList.tsx
│   ├── BrandSwitcher.tsx
│   ├── CreateBrandCard.tsx
│   └── BrandCreateDialog.tsx
├── hooks/
│   ├── useBrands.ts
│   └── useCurrentBrand.ts
├── api.ts
└── types.ts
```

---

# 77. Consultant Feature

```text
consultant/

├── components/
│   ├── ConsultantPanel.tsx
│   ├── ChatMessage.tsx
│   ├── ChatComposer.tsx
│   ├── ArtifactCard.tsx
│   ├── SuggestionCard.tsx
│   ├── ResearchPlanCard.tsx
│   ├── ResearchProgressCard.tsx
│   └── ChangeSummaryCard.tsx
├── hooks/
│   ├── useConversation.ts
│   └── useConsultant.ts
├── api.ts
└── types.ts
```

---

# 78. Research Feature

```text
research/

├── components/
│   ├── ResearchHome.tsx
│   ├── ResearchPlan.tsx
│   ├── ResearchProgress.tsx
│   ├── ResearchReport.tsx
│   ├── ResearchSource.tsx
│   ├── SourceList.tsx
│   ├── FindingCard.tsx
│   └── ResearchHistory.tsx
├── hooks/
│   ├── useResearchJob.ts
│   ├── useResearchReport.ts
│   └── useResearchStream.ts
├── api.ts
└── types.ts
```

---

# 79. Brand Feature

```text
brand/

├── Overview.tsx
├── Positioning.tsx
├── Story.tsx
├── Mission.tsx
├── Vision.tsx
├── Values.tsx
├── Tone.tsx
└── Tagline.tsx
```

---

# 80. Editor

현재 PDF Variable Sidebar를 장기적으로 Editor 시스템으로 전환한다.

```text
editor/

├── BlockEditor.tsx
├── BlockRenderer.tsx
├── TextBlock.tsx
├── HeadingBlock.tsx
├── ImageBlock.tsx
├── TableBlock.tsx
├── CalloutBlock.tsx
├── DividerBlock.tsx
└── Toolbar.tsx
```

---

# 81. Document Data Model

Raw HTML을 중심으로 저장하지 않는다.

```json
{
  "id": "doc_001",
  "brand_id": "brand_001",
  "title": "Brand Guide",
  "blocks": [
    {
      "id": "block_001",
      "type": "heading",
      "content": "Brand Story"
    },
    {
      "id": "block_002",
      "type": "paragraph",
      "content": "..."
    },
    {
      "id": "block_003",
      "type": "image",
      "asset_id": "asset_001"
    }
  ]
}
```

---

# 82. Block Editor 원칙

모든 결과를 한 번에 HTML 문자열로 생성하지 않는다.

```text
Document
→ Block
→ Block
→ Block
```

구조를 사용한다.

장점:

* 직접 편집
* AI 수정
* drag/drop
* versioning
* PDF export
* Web rendering

을 모두 쉽게 구현할 수 있다.

---

# 83. AI Editor

사용자가 Block을 선택한 상태에서 AI Consultant에:

```text
"이 문장을 더 전문적으로 바꿔줘."
```

라고 할 수 있다.

Context:

```json
{
  "document_id": "doc_001",
  "block_id": "block_009",
  "text": "..."
}
```

AI는 전체 BrandState를 다시 생성하지 않고 해당 block만 수정한다.

---

# 84. Workspace와 AI의 관계

중앙 화면:

```text
Source of Visible Truth
```

오른쪽 AI:

```text
Source of Interaction
```

즉:

```text
Workspace = 결과
AI = 조작
```

로 역할을 구분한다.

---

# 85. Dependency Graph UI

사용자가 Business/Customer를 수정하면 영향을 보여준다.

예:

```text
Target 변경

Changed:
Customer.Target

Affected:

High
→ Persona
→ Journey
→ Positioning

Medium
→ Tone
→ Key Message

Low
→ Visual Direction
```

---

# 86. Regeneration UX

AI가 자동으로 무조건 다시 생성하지 않는다.

```text
Target updated.

3개 항목이 영향을 받을 수 있습니다.

[모두 다시 생성]
[선택해서 생성]
[나중에]
```

사용자가 통제권을 유지한다.

---

# 87. Saving UX

사용자가 수정할 때:

```text
Saving...
```

잠시 후:

```text
Saved
```

실패:

```text
Save failed

[Retry]
```

를 표시한다.

---

# 88. Optimistic Update

간단한 text edit는:

```text
UI update
→ API
```

로 optimistic update를 사용할 수 있다.

반면 BrandState 전체 변경은 서버 성공을 확인하고 cache를 갱신한다.

---

# 89. Research Progress와 Query Cache

Research Job은:

```text
useQuery
```

로 polling한다.

예:

```text
refetchInterval:

job.status === "running"
? 3000
: false
```

초기 V1은 이 방식으로 충분하다.

---

# 90. Streaming 전환

후속 단계에서:

```text
SSE
```

를 추가한다.

```text
GET /api/research/jobs/:id/events
```

Frontend:

```text
useResearchStream()
```

으로 이벤트를 수신한다.

---

# 91. Responsive

## Desktop

3-column.

## Tablet

```text
Sidebar
+
Main
+
Consultant Drawer
```

## Mobile

```text
Main
```

중심.

Navigation과 Consultant는 Drawer로 전환한다.

---

# 92. Mobile AI UX

모바일에서는:

```text
[AI]
```

floating button으로 Consultant를 연다.

Drawer:

```text
┌──────────────────────┐
│ AI Consultant        │
│                      │
│ messages             │
│                      │
│                      │
│ [입력]               │
└──────────────────────┘
```

---

# 93. Login Responsive UX

로그인 화면은 모바일에서도:

```text
Full width
+
Centered Auth Card
```

구조를 유지한다.

Desktop:

```text
max-width: 420px
```

정도의 단일 카드 중심.

Mobile:

```text
padding: 16px
width: 100%
```

으로 확장한다.

---

# 94. Visual Design Direction

현재 레포는 neon gradient 중심의 UI를 사용하고 있다.

향후 Workspace는 이를 그대로 전부 유지하기보다:

```text
neutral workspace
+
brand accent
```

구조로 이동하는 것을 권장한다.

현재 HTML 프로토타입처럼 Workspace에서는:

```text
white / gray surface
+
indigo accent
```

를 사용할 수 있다.

Landing / Authentication / AI action에는 brand accent를 선택적으로 강하게 사용할 수 있다.

---

# 95. Design System

기본:

```text
Background
Surface
Border
Text
Muted Text
Primary
Accent
Danger
Success
```

을 token화한다.

예:

```text
--color-bg
--color-surface
--color-border
--color-text
--color-muted
--color-primary
--color-accent
```

---

# 96. Workspace 시각 원칙

문서형 UI는:

* 과도한 shadow 제거
* 과도한 gradient 제거
* 충분한 whitespace
* 명확한 hierarchy
* 높은 text readability

를 우선한다.

AI action에만 accent animation 등을 사용한다.

---

# 97. 기존 UI 재사용 전략

## `PdfPreviewSidebar`

향후:

```text
DocumentPreview
```

로 확장한다.

## `PdfVariableSidebar`

향후:

```text
InspectorPanel
```

으로 확장한다.

## `RightSidebar`

AI Consultant와 충돌하는 역할을 줄이고:

```text
Inspector / Context Panel
```

으로 재구성한다.

---

# 98. 기존 Section 컴포넌트 Migration

즉시 삭제하지 않는다.

```text
SectionO
SectionA
SectionB
SectionC
SectionDE
```

는 내부 Skill UI 또는 fallback UI로 유지한다.

---

# 99. O → Discovery

기존 Section O가 담당하는 기능:

```text
업종
감성
타겟
키워드
인터뷰
브랜드 후보
```

새 구조:

```text
Discovery Skill
```

---

# 100. A → Brand Strategy

기존 Section A:

```text
철학
스토리
포지셔닝
```

새 구조:

```text
Brand Strategy Skill
```

---

# 101. B → Business / Market / Customer

현재 B가 Persona/Journey에 집중되어 있지만 앞으로 확대한다.

```text
Customer
Market
Business Strategy
Competition
SWOT
TAM
SAM
SOM
```

---

# 102. C → Visual

```text
Color
Typography
Mood
Visual Direction
```

---

# 103. DE → Creative Asset

```text
Logo
Character
Image
```

---

# 104. Preview → Workspace Export

현재 Preview에서 PDF 다운로드를 중심으로 하는 기능을:

```text
Workspace
→ Export
```

로 옮긴다.

Export:

```text
PDF
PNG/JPG
Brand Kit
Document
```

---

# 105. 기존 API Migration

기존 API:

```text
/api/section-o/*
/api/section-a/*
/api/section-b/*
/api/section-c/*
/api/section-de/*
```

를 당장 삭제하지 않는다.

새 API가 안정화될 때까지 compatibility layer로 유지한다.

---

# 106. 새로운 API

```text
/api/auth/me
/api/auth/login
/api/auth/signup
/api/auth/logout

/api/brands
/api/brands/:brandId

/api/agent/chat

/api/brand/:brandId/state
/api/brand/:brandId/history

/api/research/quick
/api/research/jobs
/api/research/jobs/:id
/api/research/reports/:id

/api/documents
/api/documents/:id
/api/documents/:id/blocks

/api/assets
/api/assets/:id
```

---

# 107. Agent API

```http
POST /api/agent/chat
```

Request:

```json
{
  "brand_id": "brand_001",
  "message": "우리 타겟을 조금 더 젊게 바꿔줘.",
  "context": {
    "page": "customer"
  }
}
```

현재 인증 User 정보는 Session에서 Backend가 확인한다.

---

# 108. Agent Response UI Contract

Frontend가 AI 응답을 단순 문자열로 처리하지 않도록 한다.

```typescript
type AgentResponse = {
  message: string;
  artifacts: Artifact[];
  actions: AgentAction[];
  mutations: BrandMutation[];
  research?: ResearchJobReference;
  requiresConfirmation: boolean;
};
```

---

# 109. Agent Action

```typescript
type AgentAction = {
  id: string;
  label: string;
  type:
    | "apply"
    | "edit"
    | "regenerate"
    | "research"
    | "confirm";
};
```

---

# 110. Brand Mutation

```json
{
  "path": "brand.positioning",
  "before": "...",
  "after": "...",
  "reason": "Target changed"
}
```

Frontend는 이 값을 Change Summary Card로 보여준다.

실제 적용은 Backend 권한 검증과 승인 절차를 거친다.

---

# 111. Change Summary

```text
변경 사항

Target

20대 여성

→

20대 대학생

영향:

✓ Persona
✓ Positioning
✓ Customer Journey

[적용]
[되돌리기]
```

---

# 112. Undo

AI 변경에는 가능하면:

```text
Undo
```

를 제공한다.

이를 위해 backend에서 BrandState Snapshot을 생성한다.

```text
Snapshot Before
Mutation
Snapshot After
```

---

# 113. History 연결

모든 중요한 변경은:

```text
History
```

에 기록한다.

```json
{
  "type": "brand_mutation",
  "actor": "user",
  "path": "brand.positioning",
  "before": "...",
  "after": "...",
  "reason": "...",
  "created_at": "..."
}
```

---

# 114. Frontend File Structure

최종적으로 다음 구조를 목표로 한다.

```text
frontend/src/

├── app/
│   ├── App.tsx
│   ├── routes.tsx
│   └── providers.tsx
│
├── layouts/
│   ├── AuthLayout.tsx
│   └── WorkspaceLayout.tsx
│
├── pages/
│   ├── Landing.tsx
│   ├── Login.tsx
│   ├── Signup.tsx
│   ├── ForgotPassword.tsx
│   ├── Brands.tsx
│   └── Workspace.tsx
│
├── features/
│   ├── auth/
│   ├── brands/
│   ├── workspace/
│   ├── consultant/
│   ├── business/
│   ├── market/
│   ├── customer/
│   ├── brand/
│   ├── visual/
│   ├── assets/
│   ├── research/
│   ├── editor/
│   └── history/
│
├── api/
│   ├── client.ts
│   ├── auth.ts
│   ├── users.ts
│   ├── brands.ts
│   ├── agent.ts
│   ├── research.ts
│   ├── documents.ts
│   └── assets.ts
│
├── stores/
│   └── uiStore.ts
│
├── hooks/
│   ├── useDebounce.ts
│   └── useResponsive.ts
│
├── types/
│   ├── auth.ts
│   ├── user.ts
│   ├── brand.ts
│   ├── agent.ts
│   ├── research.ts
│   ├── document.ts
│   └── asset.ts
│
├── components/
│   └── ui/
│
└── styles/
```

---

# 115. API와 Feature 분리

Feature가 직접 Axios를 여기저기 호출하지 않는다.

나쁜 구조:

```text
Component
→ axios.post(...)
```

좋은 구조:

```text
Component
→ hook
→ api function
→ client
```

예:

```text
useResearchJob()
→ researchApi.getJob()
→ apiClient
```

---

# 116. React Query Key

예:

```typescript
["auth", "me"]

["brands"]

["brand", brandId]

["brand", brandId, "state"]

["research", brandId]

["research-job", jobId]

["research-report", reportId]

["document", documentId]

["assets", brandId]
```

---

# 117. Cache Invalidation

BrandState 변경 후:

```text
["brand", brandId, "state"]
```

를 갱신하고 영향받는 Query만 invalidate한다.

예:

```text
Target 변경

→ Customer query invalidate

→ Brand query invalidate
```

Visual이 영향받지 않는다면 다시 요청하지 않는다.

---

# 118. Logout Cache Reset

Logout 시:

```text
queryClient.clear()
```

또는 인증/사용자 데이터와 관련된 모든 Cache를 명시적으로 제거한다.

목적:

```text
User A
로그아웃
↓
User B
로그인
↓
User A 데이터가 캐시로 노출되지 않음
```

---

# 119. Deep Research와 Frontend 연결

전체 흐름:

```text
ChatComposer
      ↓
POST /api/agent/chat
      ↓
Agent
      ↓
Research Job 생성
      ↓
Chat에 ResearchPlanCard 표시
      ↓
User approve
      ↓
Research Job running
      ↓
ResearchProgressCard
      ↓
Completed
      ↓
Report
      ↓
ResearchReport page
```

---

# 120. Research Job UI 상태

```typescript
type ResearchStatus =
  | "planning"
  | "approved"
  | "queued"
  | "running"
  | "normalizing"
  | "completed"
  | "failed"
  | "cancelled";
```

상태마다 UI를 다르게 표시한다.

---

# 121. Loading 설계

전체 화면 loading을 사용하지 않는다.

나쁜 예:

```text
전체 화면

Loading...
```

좋은 예:

```text
Research Card
→ 진행 중

Workspace
→ 계속 사용 가능
```

즉 Deep Research가 실행 중이어도 사용자가 다른 Workspace를 볼 수 있어야 한다.

---

# 122. Background UX

연구가 진행 중일 때:

```text
현재 Research 1건 실행 중
```

을 Header에 표시한다.

사용자는:

```text
Market
→ Research
→ Brand
```

를 자유롭게 이동할 수 있다.

완료되면:

```text
Research completed
```

notification을 표시한다.

---

# 123. Notification

예:

```text
✓ 한국 디저트 시장 연구가 완료되었습니다.

[보고서 보기]
```

---

# 124. Mobile Notification

모바일에서는 Bottom Toast:

```text
Research complete

[보기]
```

---

# 125. Accessibility

기본 원칙:

* keyboard navigation
* focus visible
* aria labels
* 적절한 heading hierarchy
* 색상만으로 상태 구분하지 않음
* loading state text 제공
* image alt
* error message 제공

Auth 화면에도 동일한 접근성 원칙을 적용한다.

---

# 126. Error UI

API 오류:

```text
작업을 완료하지 못했어요.

[다시 시도]
```

Login 오류:

```text
이메일 또는 비밀번호를 확인해주세요.
```

Research 실패:

```text
Research를 완료하지 못했습니다.

원인:

일시적인 Research provider 오류

[다시 시도]
```

---

# 127. Empty State

Market:

```text
아직 시장 조사가 없습니다.

AI Consultant에게

"우리 시장을 조사해줘"

라고 요청해보세요.
```

Research:

```text
아직 Research가 없습니다.

[새 Research 시작]
```

Brands:

```text
아직 Brand가 없습니다.

첫 번째 브랜드를 만들어보세요.

[새 Brand 만들기]
```

---

# 128. Editor와 AI 관계

Editor는 직접 수정할 수 있어야 한다.

동시에:

```text
Block 선택
→ AI에게 수정 요청
```

도 가능해야 한다.

즉:

```text
Manual Editing
+
AI Editing
```

둘을 동등하게 제공한다.

---

# 129. Editor Action

Block 선택 후:

```text
Edit
Rewrite
Shorten
Expand
Professional
Friendly
Generate Alternative
Ask AI
```

---

# 130. Asset Editor

Logo:

```text
현재 Logo

[다시 생성]
[변형]
[배경 제거]
[다운로드]
```

Character:

```text
현재 Character

[표정 변경]
[포즈 변경]
[다시 생성]
```

단, 실제 asset mutation은 Backend Tool 권한을 사용한다.

---

# 131. Export UI

Header:

```text
Export
```

클릭:

```text
Export

PDF
PNG
Brand Guide
Brand Kit
```

PDF는 더 이상 전체 제품의 마지막 단계가 아니다.

---

# 132. 핵심 UX 변화

## Before

```text
입력
→ O
→ A
→ B
→ C
→ DE
→ PDF
```

## After

```text
Login
→ Brand
→ Conversation
→ BrandState
→ Workspace

↕

Conversation
↕

Research
↕

Edit
↕

Generate
↕

Workspace

→ Export
```

---

# 133. 핵심 Product Loop

```text
Conversation
      ↓
Agent
      ↓
Research / Generation / Edit
      ↓
Artifact
      ↓
Workspace
      ↓
User Feedback
      ↓
BrandState
      ↓
Dependency Update
      ↓
Next Conversation
```

이 루프가 NAME TAG의 핵심이다.

---

# 134. 기존 코드 Migration 전략

기존 코드를 한 번에 삭제하지 않는다.

## Stage 1

현재 기능 유지.

```text
Section O
Section A
Section B
Section C
Section DE
Preview
```

## Stage 2

Authentication + Brand Dashboard 추가.

```text
Login
Signup
Brands
Brand Switcher
```

## Stage 3

Workspace Shell 추가.

```text
WorkspaceLayout
Navigation
Consultant Panel
```

## Stage 4

기존 결과를 Workspace에서 표시.

## Stage 5

Agent가 기존 Section API를 호출하도록 만든다.

## Stage 6

Section API를 Skill 내부 구현으로 이동.

## Stage 7

기존 Section UI 제거.

---

# 135. Stage 1 — Authentication

구현:

```text
Login
Signup
Logout
Session Check
Protected Route
```

필수 E2E:

```text
Signup
→ Login
→ Brands
→ Logout
```

---

# 136. Stage 2 — Brand Context

구현:

```text
Brand Dashboard
Brand Create
Brand Switcher
Current Brand
```

E2E:

```text
User
→ Create Brand A
→ Create Brand B
→ Switch A/B
→ Data isolation 확인
```

---

# 137. Stage 3 — Workspace

WorkspaceLayout 구현.

```text
WorkspaceLayout

├── Sidebar
├── Main
└── Consultant
```

기존 Generate 페이지와 병렬로 개발한다.

---

# 138. Stage 4 — Legacy Adapter

기존 brandStore와 새로운 BrandState Adapter를 연결한다.

```text
dataA
→ brand.mission

dataA
→ brand.positioning

dataA
→ brand.story
```

등의 mapping을 만든다.

---

# 139. Migration Adapter

```typescript
function legacyToBrandState(legacy): BrandState {
  return {
    business: ...,
    market: ...,
    customer: ...,
    brand: ...,
    visual: ...
  };
}
```

기존 데이터 손실을 방지한다.

---

# 140. Stage 5 — Agent

AI Consultant가 기존 API를 호출한다.

예:

```text
사용자

"브랜드 스토리 만들어줘."

↓

Agent

↓

Brand Strategy Skill

↓

Legacy Section A service

↓

결과

↓

Artifact

↓

Workspace
```

---

# 141. Stage 6 — Skill Migration

기존 Section API의 prompt와 생성 로직을 Skill로 이동한다.

```text
Old

routers/section_a.py

↓

New

skills/brand_strategy/
```

Router는 HTTP entry point로 최소화한다.

---

# 142. 최종 Backend 연결

Frontend:

```text
Consultant
     ↓
Agent API
```

Backend:

```text
Agent
 ↓
Router
 ↓
Skill
 ↓
Tool
 ↓
BrandState
```

---

# 143. Testing Strategy

## Unit

* component
* hook
* formatter
* state logic
* auth guard

## Integration

* Login
* Session
* Brand access
* Agent response
* Research Job
* BrandState update

## E2E

```text
Landing
→ Signup
→ Login
→ Create Brand
→ Chat
→ Artifact
→ Research
→ Report
→ Apply Finding
→ Export
→ Logout
→ Login
→ 이전 Brand 확인
```

---

# 144. 사용자 격리 E2E

로그인 기능을 추가하면 아래 테스트가 필수다.

## Scenario

```text
User A
→ Brand A 생성
→ Positioning 저장
→ Logout

User B
→ 로그인
→ Brand A가 보이지 않음
```

또한:

```text
User A
→ Brand A

User B
→ Brand B
```

일 때 API나 Query Cache를 통해 서로의 데이터를 노출하지 않아야 한다.

Frontend 테스트는 Backend 권한 검증을 대체하지 않지만, 사용자 흐름에서 데이터가 섞이지 않는지 확인해야 한다.

---

# 145. Frontend MVP

### 반드시 구현

* Landing
* Login
* Signup
* Logout
* Protected Route
* Brand Dashboard
* Brand Creation
* Workspace
* Navigation
* AI Consultant
* BrandState rendering
* Artifact
* Natural language edit
* Research plan
* Research progress
* Research report
* Source
* Finding
* PDF export

---

# 146. V1에서 제외

* Figma 수준 디자인 편집
* 복잡한 Canvas
* 실시간 협업
* Multi-user presence
* 고급 animation editor
* 완전한 Canva clone
* 모바일 전용 별도 앱
* 소셜 로그인 다중 provider의 복잡한 조합

인증 구조 자체는 넣되, 초기에는 단순한 Email/Password 흐름부터 구현한다.

---

# 147. P0 개발 계획

```text
[ ] AuthLayout
[ ] Login
[ ] Signup
[ ] Logout
[ ] Session Check
[ ] Protected Route
[ ] Brand Dashboard shell
[ ] WorkspaceLayout
[ ] WorkspaceSidebar
[ ] WorkspaceHeader
[ ] ConsultantPanel shell
[ ] 새 routing
[ ] 기존 Section 기능 유지
```

---

# 148. P1 개발 계획

```text
[ ] Brand Create
[ ] Brand Switcher
[ ] Current Brand Context
[ ] BrandState API 연결
[ ] Consultant Chat
[ ] Agent API
[ ] Artifact
[ ] Apply
[ ] Natural language edit
[ ] Change Summary
[ ] History
```

---

# 149. P2 개발 계획

```text
[ ] Research UI
[ ] Research Plan
[ ] Research Progress
[ ] Research Report
[ ] Source
[ ] Finding
[ ] Apply Finding
```

---

# 150. P3 개발 계획

```text
[ ] Block Editor
[ ] AI Editor
[ ] Dependency Engine
[ ] Asset Workspace
[ ] PDF Export
[ ] Brand Kit
```

---

# 151. P4 고급 기능

```text
[ ] SSE
[ ] MCP
[ ] File Search
[ ] advanced editor
[ ] collaboration
[ ] multi-model
[ ] social login providers
[ ] advanced usage dashboard
```

---

# 152. 성능 원칙

Deep Research가 실행 중이라고 전체 Workspace가 느려져서는 안 된다.

따라서:

```text
Research Job
→ background
```

와:

```text
Workspace
→ normal interaction
```

을 분리한다.

---

# 153. Cache 전략

캐시 대상:

```text
Current User
Brands
BrandState
Research Report
Research Job
Asset List
Document
```

캐시하지 않는 상태:

```text
Modal
Drawer
Selected block
Theme
Temporary input
Password
```

---

# 154. Frontend와 Backend 책임 구분

## Frontend

```text
Display
Interaction
Local UI state
Optimistic update
Navigation
Editor
Authentication UI
```

## Backend

```text
Business logic
Authentication
Authorization
Agent
Tool
BrandState
Research
Persistence
Usage
Audit
```

Frontend에 AI 판단 로직이나 실제 접근 권한 판단 로직을 넣지 않는다.

---

# 155. Frontend와 AI의 결합도를 낮추는 방법

Frontend는:

```text
Artifact
AgentAction
BrandMutation
ResearchReference
```

와 같은 추상 타입만 이해한다.

즉 어떤 LLM을 사용하는지 몰라도 된다.

```text
Gemini
GPT
Other Model
```

모델이 변경되어도 Frontend는 동일하게 동작한다.

---

# 156. HTML Prototype 반영 사항

현재 제공된 HTML 프로토타입은 다음 UX를 기준 시안으로 사용한다.

### Authentication

```text
Login Card
Email
Password
Remember Me
Forgot Password
Signup
Theme Toggle
```

### Workspace

```text
Left Sidebar
Current Brand
Navigation
Theme
Logout
```

### Main

```text
Application Header
Save Status
Export
Document Content
Inline Editing
Ask AI
```

### AI Consultant

```text
Fixed Right Panel
AI Message
User Message
Artifact Card
Apply
Chat Composer
```

### Mobile

```text
Sidebar Drawer
AI Drawer
Overlay
Mobile Header
Floating AI Button
```

이 HTML은 최종 구현 코드가 아니라 **UX/레이아웃 reference**다.

---

# 157. HTML Prototype에서 실제 제품으로 가져갈 것

가져갈 것:

```text
Login / Workspace 전환 흐름
Theme Toggle
3-column Workspace
Current Brand UI
AI Consultant
Artifact Card
Inline Editing
Responsive Drawer
Save State
Export
```

그대로 유지하지 않는 것:

```text
HTML inline JavaScript 상태관리
document.getElementById 중심 UI 제어
브라우저 내부 가짜 login
브라우저 내부 가짜 logout
정적 Brand 데이터
정적 Artifact 적용
```

실제 React 제품에서는 모두 React State + API + TanStack Query로 대체한다.

---

# 158. Login Prototype → Production Migration

HTML Prototype:

```text
handleLogin()
→ Workspace show
```

Production:

```text
LoginForm
→ authApi.login()
→ Session 생성
→ useCurrentUser()
→ Navigate /brands
```

HTML Prototype:

```text
handleLogout()
→ Login show
```

Production:

```text
authApi.logout()
→ query cache reset
→ Navigate /login
```

---

# 159. Brand Switcher Prototype → Production

HTML Prototype:

```text
MY BRAND
▼
```

Production:

```text
useBrands()
→ BrandSwitcher
→ select brand
→ /workspace/:brandId
```

Brand 변경 시:

```text
Brand Query
Conversation Query
Research Query
Document Query
Asset Query
```

를 현재 Brand 기준으로 변경한다.

---

# 160. AI Artifact Prototype → Production

HTML Prototype:

```text
Apply Artifact
```

Production:

```text
ArtifactCard
→ approve
→ backend mutation
→ BrandState update
→ History
→ Query invalidation
```

Frontend에서 텍스트만 바꾸는 방식으로 구현하지 않는다.

---

# 161. 최종 구조

```text
Frontend

│
├── Public
│   ├── Landing
│   ├── Login
│   ├── Signup
│   └── Password Reset
│
├── Authenticated
│   │
│   ├── Brand Dashboard
│   │
│   └── Workspace
│       │
│       ├── Navigation
│       ├── Main Workspace
│       │   ├── Business
│       │   ├── Market
│       │   ├── Customer
│       │   ├── Brand
│       │   ├── Visual
│       │   ├── Research
│       │   ├── Assets
│       │   └── Editor
│       │
│       └── AI Consultant
│           ├── Chat
│           ├── Artifact
│           ├── Research Plan
│           ├── Progress
│           └── Change Summary
│
└── Global
    ├── Theme
    ├── Notifications
    └── Session
```

---

# 162. 최종 UX

사용자는:

```text
계정 생성
```

으로 시작한다.

로그인 후:

```text
내 Brand
```

를 확인한다.

새 Brand를 만들면:

```text
"이런 사업을 만들고 있어."
```

라고 시작한다.

AI가:

```text
"좋아요. 몇 가지를 확인할게요."
```

라고 질문한다.

정보가 쌓이면:

```text
Business
Customer
Brand
```

가 자동으로 만들어진다.

사용자가:

```text
"경쟁사가 어떻게 하고 있는지 조사해줘."
```

라고 하면:

```text
Research Plan
→ Deep Research
→ Report
```

가 만들어진다.

사용자가:

```text
"이걸 포지셔닝에 반영해줘."
```

라고 하면:

```text
Finding
→ Proposal
→ User Approval
→ BrandState
→ Positioning
→ Artifact
```

가 연결된다.

그리고 사용자가 계속:

```text
고치고
조사하고
비교하고
생성하고
편집하고
```

하면서 하나의 브랜드 Workspace를 발전시킨다.

---

# 163. 제품의 최종 정의

NAME TAG는:

```text
AI가 브랜드를 한 번 만들어주는 서비스
```

가 아니다.

목표는:

```text
로그인한 사용자가

자신의 Brand를 만들고

AI와 대화하면서

사업을 이해하고

시장과 고객을 조사하고

브랜드를 설계하고

결과물을 편집하고

계속 발전시킬 수 있는

AI Brand Workspace
```

이다.

---

# 164. 최종 개발 원칙

1. 기존 기능을 버리지 않는다.
2. Section을 사용자 UI에서 제거하고 내부 Skill로 이동한다.
3. BrandState를 Single Source of Truth로 사용한다.
4. User를 최상위 소유 주체로 하고 Brand를 사용자별 독립 Workspace로 관리한다.
5. 모든 Brand 데이터는 인증된 사용자와 Brand 권한 범위 안에서 접근한다.
6. Chat을 제품의 중심이 아니라 Workspace를 조작하는 인터페이스로 만든다.
7. Research는 별도 Job으로 관리한다.
8. Deep Research 결과를 자동으로 BrandState에 덮어쓰지 않는다.
9. AI가 제안하고 사용자가 승인하는 구조를 기본으로 한다.
10. Document는 Raw HTML보다 Block 기반으로 저장한다.
11. 서버 상태는 TanStack Query, UI 상태는 Zustand를 사용한다.
12. 인증 Session과 비밀번호를 일반 UI State/localStorage로 관리하지 않는다.
13. Frontend가 Agent/LLM 구현에 직접 결합되지 않도록 한다.
14. Frontend의 숨김/비활성화는 보안 수단이 아니며 실제 권한 검사는 Backend에서 수행한다.
15. Logout 시 이전 사용자의 Query Cache를 제거한다.

---

# 165. 핵심 한 줄

> **NAME TAG의 Frontend는 "AI 채팅 화면"이 아니라 "로그인한 사용자가 자신의 브랜드를 지속적으로 만들고 발전시키는 AI 작업공간"이어야 한다.**
