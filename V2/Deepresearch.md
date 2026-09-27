# NAME TAG — Deep Research Product & Technical Specification

> 개정판: Multi-user / Authentication 반영


## 문서 목적

이 문서는 NAME TAG의 **Deep Research 기능만을 독립적으로 정의**한다.

중요:

> Deep Research는 NAME TAG 전체 개발의 선행 단계가 아니라, 기본 Persistence / BrandState / Skill / Quick Research / Agent 기반이 안정된 이후 구현하는 Research Engine의 고급 실행 모드다.

핵심 원칙:

> **Research는 검색 기능이 아니라 브랜드 의사결정을 위한 근거 생산 시스템이다.**

---


---

# 0-A. Multi-user Research Scope

Deep Research는 사용자 인증이 없는 독립적인 웹 검색 기능이 아니다. NAME TAG에서는 Research Job 자체가 **사용자와 Brand에 귀속되는 서버 리소스**다.

```text
Authenticated User
       ↓
Brand Membership
       ↓
Research Job
       ↓
Research Report / Source / Finding
```

따라서 같은 `research_id`를 알고 있다는 이유만으로 다른 사용자가 Report를 조회할 수 없어야 한다.

## 기본 필드

```text
ResearchJob
├── id
├── brand_id
├── created_by
├── approved_by
├── applied_by
├── status
└── created_at
```

`created_by`, `approved_by`, `applied_by`는 서로 다른 사용자가 될 수 있다. 초기 개인 사용에서는 대부분 동일하지만 향후 Team Workspace에서 중요해진다.

## 역할별 Research 권한

| Role | Plan | Start | View | Apply Finding | Cancel |
|---|---:|---:|---:|---:|---:|
| owner | ✅ | ✅ | ✅ | ✅ | ✅ |
| editor | ✅ | ✅ | ✅ | ✅ | 본인 Job 중심 |
| viewer | ❌ | ❌ | ✅ | ❌ | ❌ |

실제 API에서는 Role 외에도 해당 작업을 생성했는지, 현재 Job 상태가 무엇인지 검증한다.

## 비용이 발생하는 기능

다음 기능은 인증된 사용자만 실행하도록 한다.

```text
Quick Research
Deep Research
Image Generation
File Upload
Export
```

이는 기능 제한뿐 아니라 외부 API 비용 남용을 막기 위한 운영상의 기준이다.

# 1. 문서 목적

Deep Research는 단순한 "웹 검색 + AI 요약" 기능으로 구현하지 않는다.

사용자의 사업과 브랜드 맥락을 이해하고, 복합적인 질문을 연구 계획으로 분해하고, 다중 출처를 조사/비교하며, 검증 가능한 보고서와 Finding을 생성한다.

전체 흐름:

```text
사용자 질문
 ↓
Research Mode 판단
 ↓
Quick 또는 Deep
 ↓
Research Plan
 ↓
사용자 승인
 ↓
Research Job
 ↓
다중 출처 수집 / 비교
 ↓
Raw Report
 ↓
Normalization
 ↓
Research Finding
 ↓
Strategic Implication
 ↓
Brand Change Proposal
 ↓
사용자 승인
 ↓
BrandState
```

---

# 2. Deep Research의 제품 정의

Deep Research는 다음을 수행하는 **Research Skill의 전문 실행 모드**다.

> 사용자의 사업과 브랜드 맥락을 이해하고, 복합적인 질문을 스스로 연구 계획으로 분해한 뒤 웹과 필요한 외부 자료를 조사하고, 근거가 있는 보고서와 실행 가능한 인사이트를 생성한다.

일반 Chat AI:

```text
질문
→ 답변
```

NAME TAG Deep Research:

```text
질문
→ 계획
→ 조사
→ 검증
→ 비교
→ 보고서
→ Finding
→ 인사이트
→ 변경 Proposal
```

---

# 3. NAME TAG에서 Research가 필요한 이유

외부 근거가 필요한 영역:

* 시장 규모
* 시장 성장률
* 시장 구조
* 경쟁사
* 경쟁사 가격
* 경쟁사 포지셔닝
* 소비자 트렌드
* 소비자 행동
* 산업 변화
* 정책/규제
* 기술 변화
* 해외 시장
* 유사 서비스
* 비즈니스 모델
* 고객 세그먼트

원칙:

> 변동성이 있는 사실은 Research를 통해 외부 근거를 확보한다.

특히 시장 규모, 가격, 성장률, 경쟁사 수치 등은 근거 없는 추정을 사실처럼 저장하지 않는다.

---

# 4. Quick Research와 Deep Research의 구분

## 4.1 Quick Research

### 목적

간단한 최신 정보 확인 또는 짧은 정보 수집.

### 특징

* 낮은 latency
* 적은 검색
* 짧은 결과
* 즉시 답변
* Research Job 없이 완료할 수도 있음

### 예시

```text
"스타벅스의 현재 아메리카노 가격 알려줘."

"한국에서 비슷한 서비스 5개 찾아줘."

"최근 디저트 트렌드 알려줘."

"이 경쟁사의 공식 홈페이지 찾아줘."
```

### 처리

```text
User
 → Agent
 → Search Tool
 → Source
 → LLM
 → Answer
```

필요하면 결과를 Research DB에 저장한다.

---

# 5. Deep Research

## 5.1 목적

다수의 출처를 검색하고 읽고 비교해야 하는 복합적인 조사.

예:

```text
"한국 디저트 시장의 규모와 성장률을 조사하고
주요 경쟁사의 가격, 타겟, 포지셔닝을 비교해줘."
```

```text
"20대 대학생을 타겟으로 이 서비스를 시작할 때
시장성이 있는지 조사해줘."
```

```text
"국내외 유사 서비스 15개를 조사해서
사업 모델, 가격, 타겟, 차별점을 비교해줘."
```

---

# 6. Deep Research의 기술적 특징

NAME TAG에서는 다음과 같은 비동기 Research Job 구조를 사용한다.

```text
API Request
 ↓
Research Job
 ↓
Background Execution
 ↓
Polling (V1)
 ↓
Report
```

실시간 streaming은 이후 SSE 단계에서 추가한다.

Deep Research 원본 결과와 NAME TAG 내부 표준 구조화 결과를 분리한다.

```text
Raw Research Output
 ↓
Normalizer
 ↓
ResearchReport
ResearchSource
ResearchFinding
```

---

# 7. NAME TAG Deep Research 전체 아키텍처

```text
┌────────────────────────────────────────────────────┐
│                    Frontend                       │
│                                                    │
│ AI Consultant                                      │
│ Research Plan                                      │
│ Research Progress                                  │
│ Research Report                                    │
│ Findings                                           │
│ Sources                                            │
└─────────────────────────┬──────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│                    FastAPI                         │
│                                                    │
│ Research Router                                    │
│ Research Service                                   │
│ Research Job Manager                               │
│ Research Normalizer                                │
│ Agent / Research Skill                             │
└─────────────────────────┬──────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│              Gemini Interactions / Model          │
│                                                    │
│ Quick Research                                     │
│ Deep Research                                      │
└─────────────────────────┬──────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────┐
│                    Database                        │
│                                                    │
│ ResearchJob                                        │
│ ResearchReport                                     │
│ ResearchSource                                     │
│ ResearchFinding                                    │
│ ResearchEvent                                      │
└────────────────────────────────────────────────────┘
```

---

# 8. Agent 역할

Deep Research 자체를 NAME TAG의 전체 Agent로 정의하지 않는다.

중앙 Agent:

```text
AI Consultant / Brand Manager Agent
              │
              ├── Discovery Skill
              ├── Brand Strategy Skill
              ├── Customer Skill
              ├── Visual Skill
              └── Research Skill
                        │
                        ├── Quick Research
                        └── Deep Research
```

사용자는 "Deep Research Agent"를 직접 조작하지 않고:

> "시장성을 제대로 조사해줘."

처럼 요청한다.

---

# 9. Research Router

AI가 사용자 요청을 분석하여 Research mode를 결정한다.

## NONE

외부 정보가 필요하지 않음.

```text
"내 브랜드 스토리를 좀 더 감성적으로 바꿔줘."
```

## QUICK

간단한 최신 정보가 필요함.

```text
"경쟁사 3개 알려줘."
```

## DEEP

다중 출처 비교와 장문의 분석이 필요함.

```text
"시장 진입 가능성을 제대로 분석해줘."
```

---

# 10. Research Mode 판단 기준

## QUICK 조건

다음 특성을 대부분 만족하면 Quick Research.

* 단순 사실 확인
* 단일 주제
* 결과가 짧아도 충분
* 비교 대상이 적음
* 전략적 영향이 낮음
* 적은 수의 출처로 확인 가능

## DEEP 조건

다음 중 하나 이상이면 Deep 후보.

* 여러 질문을 동시에 해결
* 여러 출처 비교
* 경쟁사 분석
* 시장 분석
* 시장 규모
* 타겟 고객 검증
* 트렌드 분석
* 사업 모델 비교
* 해외 시장 비교
* 진입 가능성 분석
* 전략적 의사결정
* 장문 보고서 필요

---

# 11. 사용자가 명시적으로 Deep Research를 요구하는 경우

사용자가 직접:

```text
"딥 리서치해줘."
"제대로 조사해줘."
"깊게 조사해줘."
"출처까지 조사해줘."
"시장성을 검증해줘."
```

라고 요청하면 Deep 후보로 우선 분류한다.

다만 비용/실행시간과 범위를 고려하여 실제 실행 전에 Plan을 생성할 수 있다.

---

# 12. Deep Research 시작 UX

사용자가 요청하면 바로 긴 작업을 시작하지 않는다.

먼저 Research Plan을 제시한다.

```text
┌──────────────────────────────────────────────┐
│ Deep Research                                │
│                                              │
│ 한국 디저트 시장 진입 가능성 조사           │
│                                              │
│ 조사 질문                                    │
│ 1. 시장 규모                                 │
│ 2. 최근 성장률                               │
│ 3. 주요 경쟁사                               │
│ 4. 경쟁사 가격                               │
│ 5. 핵심 고객                                 │
│ 6. 최근 소비 트렌드                          │
│                                              │
│ 조사 범위                                    │
│ ✓ 시장                                       │
│ ✓ 경쟁사                                     │
│ ✓ 가격                                       │
│ ✓ 고객                                       │
│ ✓ 트렌드                                     │
│                                              │
│ [계획 수정]              [조사 시작]         │
└──────────────────────────────────────────────┘
```

---

# 13. Research Plan 구조

```json
{
  "title": "한국 디저트 시장 진입 가능성 조사",
  "objective": "20대 고객을 대상으로 한 디저트 브랜드의 시장 진입 가능성 분석",
  "questions": [
    "시장 규모",
    "시장 성장률",
    "주요 경쟁사",
    "가격대",
    "소비자 트렌드"
  ],
  "scope": [
    "국내 시장",
    "최근 3~5년",
    "20대 소비자",
    "주요 경쟁 브랜드"
  ],
  "sources": [
    "공공 데이터",
    "산업 보고서",
    "기업 공식 자료",
    "신뢰할 수 있는 뉴스/미디어",
    "시장 조사 자료"
  ],
  "output": {
    "type": "market_analysis",
    "format": "report"
  }
}
```

---

# 14. Research Plan 승인 흐름

```text
Create Plan
    ↓
사용자 검토
    ↓
수정?
 ┌───────┐
 │       │
Yes     No
 │       │
 ▼       ▼
Update  Approve
         ↓
       Create Job
```

사용자가 승인하기 전에는 비용이 큰 Deep Research 실행을 시작하지 않는 것을 기본으로 한다.

---

# 15. Research Job

```json
{
  "id": "research_001",
  "brand_id": "brand_001",
  "mode": "deep",
  "status": "planning",
  "plan": {},
  "progress": {},
  "created_at": "2026-09-27T12:00:00+09:00"
}
```

---

# 16. Research Job 상태

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

# 17. State Machine

```text
planning
   ↓
approved
   ↓
queued
   ↓
running
   ↓
normalizing
   ↓
completed
```

실패:

```text
running
 ↓
failed
```

취소:

```text
queued/running
 ↓
cancelled
```

---

# 18. Gemini Interaction 연결

현재 NAME TAG의 Gemini service를 활용하여 Deep Research 전용 실행 경로를 추가한다.

중요한 점:

> Interactions API 자체를 새로 도입하는 프로젝트가 아니라, 기존 Gemini Interactions 기반 호출 구조에 Deep Research/background 실행을 확장하는 작업이다.

구조:

```text
ResearchService
 ↓
Gemini Gateway / Service
 ↓
Interactions API
 ↓
Deep Research
```

Deep Research의 원본 응답은 먼저 보존하고 이후 Normalizer가 내부 schema로 변환한다.

---

# 19. Deep Research 실행

```text
Research Job
 ↓
Start
 ↓
Background Execution
 ↓
Research Progress
 ↓
Raw Result
 ↓
Normalization
 ↓
Report / Sources / Findings
```

---

# 20. Background Execution

Deep Research는 장시간 실행될 수 있으므로 요청/응답 한 번으로 끝내는 API로 설계하지 않는다.

사용자 요청:

```http
POST /api/research/jobs
```

Response:

```json
{
  "job_id": "research_001",
  "status": "queued"
}
```

이후 별도의 status 조회로 진행 상태를 확인한다.

---

# 21. 결과 확인 방법

## Polling

V1 기본 방식.

```text
GET /api/research/jobs/{id}\n
> 현재 사용자가 접근 가능한 Brand의 Job인지 서버에서 검증
```

장점:

* 구현 단순
* 재접속 쉬움
* 상태 복구가 쉬움

## Streaming

후속 단계에서 SSE로 추가한다.

```text
GET /api/research/jobs/{id}\n
> 현재 사용자가 접근 가능한 Brand의 Job인지 서버에서 검증/events
```

---

# 22. NAME TAG의 Streaming 전략

V1:

```text
Research Job
+
Polling
```

후속:

```text
Research Job
+
SSE
```

초기에는 실시간성보다 Job lifecycle과 재접속 안정성을 우선한다.

---

# 23. Research Progress UX

사용자에게 내부 추론을 그대로 보여주지 않는다.

대신 이해 가능한 진행 상태만 제공한다.

```text
Deep Research 진행 중

✓ 연구 범위 설정
✓ 시장 규모 자료 수집
✓ 경쟁사 자료 수집
● 가격/고객 데이터 비교
○ 인사이트 정리
○ 보고서 작성

수집 출처: 27개
상태: 연구 진행 중
```

---

# 24. Research Event

```json
{
  "event_id": "event_102",
  "job_id": "research_001",
  "type": "research_progress",
  "stage": "source_collection",
  "message": "경쟁사 관련 자료를 수집하고 있습니다.",
  "created_at": "2026-09-27T12:00:00+09:00"
}
```

Event type:

```text
job_created
plan_created
plan_updated
job_approved
research_started
research_progress
source_found
analysis_started
report_generation
research_completed
research_failed
normalization_started
normalization_completed
finding_created
```

---

# 25. Research Report

Deep Research 결과는 ResearchReport로 저장한다.

```json
{
  "id": "report_001",
  "research_job_id": "research_001",
  "title": "한국 디저트 시장 분석",
  "executive_summary": "...",
  "sections": [],
  "findings": [],
  "sources": [],
  "status": "completed",
  "created_at": "2026-09-27T12:30:00+09:00"
}
```

---

# 26. Report 표준 구조

```text
Research Report

1. Executive Summary
2. Research Questions
3. Market Overview
4. Market Size
5. Market Growth
6. Customer
7. Competitors
8. Pricing
9. Trends
10. Opportunities
11. Risks
12. Strategic Implications
13. Limitations
14. Sources
```

---

# 27. Executive Summary

다음 질문에 답해야 한다.

```text
무엇을 조사했는가?
무엇을 발견했는가?
가장 중요한 사실은 무엇인가?
어떤 불확실성이 존재하는가?
브랜드에 어떤 의미가 있는가?
```

---

# 28. Research Finding

Report 전체를 BrandState에 넣지 않는다.

핵심 사실/발견을 Finding으로 추출한다.

```json
{
  "id": "finding_001",
  "report_id": "report_001",
  "statement": "...",
  "evidence": "...",
  "source_ids": ["source_001", "source_004"],
  "confidence": "supported",
  "suggested_fields": [
    "customer.needs",
    "brand.positioning"
  ],
  "applied": false
}
```

---

# 29. Finding의 중요한 원칙

Finding은 단순한 AI 문장이 아니다.

```text
주장
+
근거
+
출처
+
해석 범위
```

를 가진 구조화된 객체다.

---

# 30. Confidence

초기 분류:

```text
supported
partially_supported
uncertain
contradictory
insufficient_evidence
```

Confidence는 추천 점수나 사용자 평가 점수가 아니라 **근거 상태**를 표시한다.

---

# 31. Source Model

```json
{
  "id": "source_001",
  "report_id": "report_001",
  "url": "https://...",
  "title": "Source Title",
  "publisher": "Publisher",
  "published_at": null,
  "accessed_at": "2026-09-27T12:20:00+09:00",
  "source_type": "official",
  "citation": {},
  "relevance": "high"
}
```

Source type:

```text
official
government
research
company
news
community
blog
unknown
```

---

# 32. Citation 처리

Research 결과에서 가능한 경우 주장과 출처의 관계를 유지한다.

```text
주장 [1][2]
```

내부:

```json
{
  "claim": "시장 규모가 성장하고 있다.",
  "source_ids": ["source_001", "source_002"]
}
```

Citation은 단순 URL 목록이 아니라 **어떤 주장에 어떤 출처가 연결되는지**를 표현하는 데 초점을 둔다.

---

# 33. Citation UI

Report:

```text
한국 디저트 시장은 최근 몇 년 동안 성장세를 보이고 있다. [1][2]
```

Source Drawer:

```text
Sources

[1] 공공기관 보고서
    출처 보기 →

[2] 산업 연구기관
    출처 보기 →
```

Finding Card:

```text
Finding

"시장 규모가 성장하고 있다."

Evidence
[1] [2] [3]

근거 보기 →
```

---

# 34. Research → BrandState 연결

Deep Research의 핵심은 조사 결과를 자동 복사하는 것이 아니다.

```text
Research
   ↓
Finding
   ↓
Suggested Application
   ↓
Brand Change Proposal
   ↓
User Approval
   ↓
BrandState Mutation
```

---

# 35. 자동 적용을 금지하는 이유

Research 결과가 곧 브랜드 전략이라는 보장은 없다.

예:

```text
Finding:
친환경 포장 수요 증가
```

라고 해서:

```text
brand.values += "친환경"
```

을 자동 실행하지 않는다.

트렌드와 브랜드 의사결정은 서로 다른 층위이기 때문이다.

---

# 36. Research Finding Application UX

```text
┌────────────────────────────────────────────┐
│ Research Finding                           │
│                                            │
│ 소비자가 경험 요소를 중요하게 평가         │
│                                            │
│ 근거                                       │
│ [Source 03] [Source 07] [Source 11]       │
│                                            │
│ AI 제안                                    │
│ Customer Needs에 추가                     │
│ Positioning 재검토                         │
│                                            │
│ [Customer에 적용]                          │
│ [Positioning에 적용]                       │
│ [저장만 하기]                              │
└────────────────────────────────────────────┘
```

---

# 37. Strategic Implications

Research에서 중요한 섹션이다.

```text
Finding
 ↓
Strategic Implication
 ↓
Suggested Action
```

단, 이것은 **전략적 해석**이지 출처가 직접 말한 사실과 동일하지 않다.

---

# 38. Fact / Analysis / Recommendation 구분

## Fact

출처가 뒷받침하는 정보.

## Analysis

수집한 정보를 비교/해석한 내용.

## Recommendation

NAME TAG가 사용자에게 제안하는 전략적 행동.

예:

```text
Fact
20대 소비자의 특정 행동 비중 증가 [1]

Analysis
경험 중심 구매가 중요한 요소일 가능성이 있음

Recommendation
브랜드 경험을 Positioning 요소로 검토
```

---

# 39. Research Prompt 정책

```text
1. 근거 없는 수치를 사실처럼 생성하지 않는다.
2. 확인할 수 없는 정보는 확인 불가라고 명시한다.
3. 최신성이 중요한 정보는 최신 자료를 우선한다.
4. 주장과 출처의 연결을 유지한다.
5. 서로 다른 출처가 충돌하면 차이를 명시한다.
6. 사실과 해석을 구분한다.
7. 조사 범위를 벗어난 결론을 확대하지 않는다.
8. 시장 규모를 임의로 계산해 사실처럼 표시하지 않는다.
9. 날짜가 중요한 정보는 발행일과 조사일을 기록한다.
10. 불확실성이 있으면 명시한다.
```

---

# 40. TAM / SAM / SOM 처리 정책

잘못된 방식:

```text
"시장 규모가 10조니까
20대 시장은 2조다."
```

올바른 방식:

```text
TAM
→ 출처 기반 전체 시장 규모

SAM
→ 타겟 지역/제품/고객 범위에 대한 근거

SOM
→ 실제 진입 가능성에 대한 가정 + 계산
```

SOM에는 다음을 표시한다.

```text
Source
Assumption
Calculation
Uncertainty
```

---

# 41. Research API

모든 Research API는 인증된 세션을 필요로 하며, `brand_id`와 현재 사용자의 `BrandMember` 관계를 서버에서 확인한다.

## Quick Research

```http
POST /api/research/quick
Cookie: session=...
```

## Plan

```http
POST /api/research/plan
Cookie: session=...
```

## Create Job

```http
POST /api/research/jobs
Cookie: session=...
```

## Approve

```http
POST /api/research/jobs/{id}/approve
```

## Status

```http
GET /api/research/jobs/{id}\n
> 현재 사용자가 접근 가능한 Brand의 Job인지 서버에서 검증
```

## Events

```http
GET /api/research/jobs/{id}\n
> 현재 사용자가 접근 가능한 Brand의 Job인지 서버에서 검증/events
```

## Cancel

```http
POST /api/research/jobs/{id}/cancel\n
> Job 생성자 또는 허용된 Brand role인지 검증
```

## Report

```http
GET /api/research/reports/{id}\n
> Report가 속한 Brand의 membership 확인
```

## Apply Finding

```http
POST /api/research/reports/{id}/apply\n
> Brand edit 권한 + 사용자 승인 필요
```

## Refresh

```http
POST /api/research/reports/{id}/refresh
```

---


---

# 41-A. Research Usage / Audit

Research가 실행될 때 시스템은 별도의 UsageEvent를 자동 기록한다. 이를 AI Tool로 노출하지 않는다.

```text
UsageEvent
├── user_id
├── brand_id
├── research_job_id
├── mode
├── model
├── sources_count
├── duration_ms
├── status
└── created_at
```

또한 중요한 상태 변경을 AuditLog로 기록한다.

```text
plan_approved
job_started
job_cancelled
finding_applied
report_refreshed
```

이렇게 하면 사용량 분석과 보안/변경 추적을 분리할 수 있다.

# 42. API Response 예시

```json
{
  "id": "research_001",
  "status": "running",
  "mode": "deep",
  "progress": {
    "stage": "source_collection",
    "label": "경쟁사 자료 수집 중",
    "sources_found": 17
  }
}
```

---

# 43. Research Tool Registry

## READ

```text
get_research_job
get_research_report
get_research_sources
get_research_findings
```

## WRITE

```text
create_research_job
save_research_report
save_research_source
save_research_finding
```

## ACTION

```text
approve_research_plan
start_research_job
apply_research_finding
refresh_research
cancel_research
```

---

# 44. Skill 구조

```text
skills/
└── research/
    ├── router.py
    ├── quick.py
    ├── deep.py
    ├── planner.py
    ├── normalizer.py
    ├── findings.py
    └── prompts.py
```

---

# 45. Research Skill

```python
class ResearchSkill:

    async def execute(self, context):
        mode = self.router.classify(context)

        if mode == "quick":
            return await self.quick.execute(context)

        if mode == "deep":
            return await self.deep.execute(context)
```

Research Skill은 Research mode와 실행 흐름을 관리하고, 실제 웹/비동기 작업은 Tool/Service를 호출한다.

---

# 46. Deep Research Service

```text
ResearchService
│
├── create_job()
├── create_plan()
├── approve_plan()
├── start_job()
├── get_job()
├── get_events()
├── cancel_job()
├── normalize_report()
├── extract_findings()
├── save_sources()
├── propose_application()
├── apply_finding()
└── refresh()
```

---

# 47. Normalization 단계

Deep Research 원본 결과를 바로 Frontend에 전달하지 않는다.

```text
Gemini Raw Output
       ↓
Normalizer
       ↓
ResearchReportSchema
ResearchFindingSchema
ResearchSourceSchema
       ↓
Database
       ↓
Workspace
```

정규화 모델 예:

```python
class ResearchFinding(BaseModel):
    statement: str
    evidence: str
    source_ids: list[str]
    confidence: str
    suggested_fields: list[str]
```

---

# 48. Deep Research + 사용자 업로드 자료

향후 다음 자료를 Research input으로 사용할 수 있다.

* 사업계획서
* 설문 결과
* 경쟁사 자료
* PDF
* 인터뷰
* 시장조사 자료

구조:

```text
User Document
 ↓
File / Storage
 ↓
Research Input
 ↓
Deep Research
 ↓
External Sources + Internal Documents
 ↓
Report
```

이 기능은 기본 Deep Research가 안정된 이후 RAG/File Search 단계에서 확장한다.

---

# 49. Research History

모든 Research를 저장한다.

```text
Research History

2026-09-27
한국 디저트 시장 분석
✓ Completed

2026-09-24
경쟁사 가격 비교
✓ Completed
```

각 Research는 다시 열 수 있어야 한다.

---

# 50. Re-Research

시장 정보는 변화하므로 Report에는 조사 일자를 기록한다.

```text
마지막 조사:
2026-09-27
```

다음 기능을 제공한다.

```text
[최신 정보로 다시 조사]
```

Re-research는 기존 Report를 무조건 덮어쓰기보다 새 버전을 생성하는 것을 기본으로 한다.

```text
Report v1
 ↓
Re-research
 ↓
Report v2
```

---

# 51. Deep Research 구현 단계

이 단계들은 **NAME TAG 전체 Phase가 아니라 Deep Research 내부 Phase**다.

## DR-1 — Data Models

```text
ResearchJob
ResearchReport
ResearchSource
ResearchFinding
ResearchEvent
```

추가 metadata:

```text
brand_id
created_by
approved_by
applied_by
```

모든 Research 모델에는 Brand ownership을 추적할 수 있는 관계를 둔다.

## DR-2 — Quick Research 연계

기존 Search Tool과 Source 구조를 정리한다.

## DR-3 — Research Plan

Plan 생성/수정/승인 API를 구현한다.

## DR-4 — Deep Research Job

background Job 생성 및 상태 lifecycle을 구현한다.

## DR-5 — Polling

Job status/event 조회 API와 UI를 구현한다.

## DR-6 — Report

원본 결과 저장 + Report schema 정규화를 구현한다.

## DR-7 — Finding

Report에서 핵심 Finding을 추출한다.

## DR-8 — Proposal

Finding을 BrandState 변경 Proposal로 변환한다.

## DR-9 — Approval

사용자가 적용 범위를 선택할 수 있도록 한다.

## DR-10 — BrandState Application

승인된 Finding만 Mutation으로 적용한다.

## DR-11 — Re-search

기존 Report의 최신화/버전 관리를 구현한다.

## DR-12 — SSE

Polling이 안정된 이후 SSE Streaming을 추가한다.

---



## DR-13 — Authorization / Usage Hardening

Deep Research 기능 공개 전에 반드시 다음을 검증한다.

```text
User A → User B Job 조회 ❌
User A → User B Report 조회 ❌
Viewer → Research start ❌
Editor → Research apply ✅
Owner → cancel ✅
```

또한 동일 사용자가 반복해서 비용이 큰 Job을 생성하는 경우를 대비해 사용자/Brand 단위 Rate Limit과 Usage Limit을 추가할 수 있도록 한다.

# 52. Deep Research 완료 기준

* User가 복합적인 조사를 요청할 수 있다.
* AI가 Research Plan을 생성할 수 있다.
* 사용자가 Plan을 수정/승인할 수 있다.
* 연구가 비동기로 실행된다.
* 진행 상태를 조회할 수 있다.
* Report와 Source가 저장된다.
* Finding이 구조화된다.
* Fact / Analysis / Recommendation이 구분된다.
* Finding에서 BrandState 변경 Proposal을 만들 수 있다.
* 사용자가 적용 여부를 선택할 수 있다.
* 적용된 변화는 History에 기록된다.
* 동일 Research를 다시 실행해 버전으로 관리할 수 있다.

---

# 53. NAME TAG 전체 시스템과의 관계

Deep Research는 다음 구조 안에 포함된다.

```text
AI Consultant
 ↓
Agent
 ↓
Research Skill
 ├── Quick Research
 └── Deep Research
        ↓
      Report
        ↓
     Finding
        ↓
    Proposal
        ↓
      Approval
        ↓
    BrandState
```

따라서 Deep Research는 제품 전체와 분리된 또 하나의 Agent가 아니라 **NAME TAG Agent가 사용할 수 있는 전문 Research Capability**다.


---

# 53-A. Authentication과의 관계

전체 시스템에서는 Authentication이 Agent보다 상위 계층에 있다.

```text
User Session
 ↓
Current User
 ↓
Brand Membership
 ↓
AI Consultant / Agent
 ↓
Research Skill
 ├── Quick Research
 └── Deep Research
 ↓
Report / Finding
 ↓
Approval
 ↓
BrandState
```

Agent와 Research는 절대로 인증 경계를 우회하지 않는다.
