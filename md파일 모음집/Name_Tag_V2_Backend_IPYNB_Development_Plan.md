# NAME TAG V2 — Backend + Jupyter Notebook 개발 계획서

## 0. 목적

NAME TAG V2는 **Backend를 먼저 완성하고, Jupyter Notebook(`.ipynb`)에서 개발자가 각 기능을 직접 실행·관찰·검증한 뒤 Frontend를 연결**한다.

핵심 흐름:

```text
Backend 코드 작성
    ↓
Notebook에서 함수 실행
    ↓
결과 확인
    ↓
DB 변화 확인
    ↓
API 호출
    ↓
실패 케이스 확인
    ↓
pytest로 고정
    ↓
다음 기능 개발
```

Notebook은 단순 문서가 아니라 **개발 과정에서 Backend를 직접 관찰하는 개발 콘솔**로 사용한다.

---

# 1. Backend 개발 원칙

## 1-1. 완료 기준

파일이 존재한다고 완료된 것으로 보지 않는다.

각 기능은 아래를 모두 통과해야 한다.

```text
[ ] Python 함수 구현
[ ] Service 연결
[ ] API Router 연결
[ ] DB 저장/조회 확인
[ ] 정상 케이스 테스트
[ ] 실패 케이스 테스트
[ ] Notebook 수동 검증
[ ] pytest 자동 테스트
```

## 1-2. 개발 순서

```text
DB
 ↓
Auth
 ↓
Brand
 ↓
BrandState
 ↓
Conversation
 ↓
LLM Service
 ↓
Skills
 ↓
Agent
 ↓
Tools
 ↓
Quick Research
 ↓
Artifact
 ↓
Asset
 ↓
Deep Research
 ↓
Export
 ↓
Backend E2E
 ↓
Frontend
```

---

# 2. Notebook 디렉터리

```text
V2/Name_Tag/
├── backend/
├── notebooks/
│   ├── 00_backend_environment.ipynb
│   ├── 01_database.ipynb
│   ├── 02_auth.ipynb
│   ├── 03_brand.ipynb
│   ├── 04_brand_state.ipynb
│   ├── 05_conversation.ipynb
│   ├── 06_llm_service.ipynb
│   ├── 07_skills.ipynb
│   ├── 08_agent.ipynb
│   ├── 09_tools.ipynb
│   ├── 10_quick_research.ipynb
│   ├── 11_artifact.ipynb
│   ├── 12_asset.ipynb
│   ├── 13_deep_research.ipynb
│   ├── 14_export.ipynb
│   └── 99_backend_e2e.ipynb
└── tests/
```

---

# 3. 모든 Notebook의 공통 구조

각 Notebook은 동일한 형식을 사용한다.

```text
1. 목표
2. 개발 대상 파일
3. 환경 확인
4. 필요한 객체 import
5. 최소 실행
6. 정상 케이스
7. 결과 출력
8. DB 상태 확인
9. 실패 케이스
10. API 테스트
11. 테스트 결과 정리
12. 다음 단계 조건
```

Markdown Cell에서는 **왜 만드는지**, Code Cell에서는 **실제로 무엇을 실행하는지**를 명확하게 구분한다.

---

# 4. `00_backend_environment.ipynb`

## 목표

Notebook에서 NAME TAG Backend 자체를 불러올 수 있는지 확인한다.

## 검증 순서

```text
Python 버전
 ↓
프로젝트 경로
 ↓
환경변수
 ↓
Backend import
 ↓
DB 연결
 ↓
FastAPI app
 ↓
/health
```

## 예시

```python
from backend.app import app
from backend.db import engine

print(app)

with engine.connect() as conn:
    print("DB connection OK")
```

## 완료 조건

```text
[ ] Backend import 성공
[ ] DB 연결 성공
[ ] FastAPI app import 성공
[ ] /health 성공
```

---

# 5. `01_database.ipynb`

## 목표

SQLAlchemy 모델과 Migration이 실제로 동작하는지 확인한다.

## 테스트 순서

```text
DB 연결
 ↓
Table 확인
 ↓
User 생성
 ↓
User 조회
 ↓
Brand 생성
 ↓
Brand 조회
 ↓
관계 확인
```

특히 **생성 전/후 DB 상태가 실제로 바뀌는지** Notebook 출력으로 확인한다.

예:

```text
Before: User count = 0
Create User
After : User count = 1
```

---

# 6. `02_auth.ipynb`

## 목표

회원가입·비밀번호 해시·로그인·JWT를 함수 수준에서 먼저 검증한다.

## 테스트

```python
hashed = hash_password("password123")

print(verify_password("password123", hashed))
print(verify_password("wrong", hashed))
```

예상:

```text
True
False
```

JWT:

```python
token = create_access_token({"sub": str(user.id)})
print(token)
```

## 실패 케이스

```text
중복 이메일
잘못된 비밀번호
존재하지 않는 사용자
토큰 없음
잘못된 토큰
```

---

# 7. `03_brand.ipynb`

## 목표

Brand CRUD를 직접 실행하고 DB에서 결과를 확인한다.

## 순서

```text
Brand 생성
 ↓
Brand 조회
 ↓
Brand 수정
 ↓
Brand 목록 조회
 ↓
Brand 삭제
```

## 필수 검증

User A가 만든 Brand를 User B가 조회할 수 없어야 한다.

```text
Authorization
+
Ownership Check
```

---

# 8. `04_brand_state.ipynb`

## 가장 중요한 Notebook

BrandState를 NAME TAG의 **Single Source of Truth**로 보고 실제 저장/조회/부분 수정까지 검증한다.

## 기본 흐름

```text
초기 BrandState 조회
 ↓
Business 수정
 ↓
DB 저장
 ↓
다시 조회
 ↓
변경 확인
```

예:

```python
update_brand_state(
    brand.id,
    {
        "business": {
            "industry": "AI",
            "service": "AI Brand Workspace"
        }
    }
)
```

## 반드시 확인할 것

Business를 수정했을 때 Customer / Brand / Visual 등 다른 section이 의도치 않게 사라지지 않아야 한다.

---

# 9. `05_conversation.ipynb`

## 목표

AI Consultant의 대화 데이터를 서버에 저장하고 다시 조회한다.

## 순서

```text
Conversation 생성
 ↓
User Message 저장
 ↓
Assistant Message 저장
 ↓
Conversation 조회
 ↓
Messages 조회
```

서버를 재시작해도 DB의 데이터가 남아 있어야 한다.

---

# 10. `06_llm_service.ipynb`

## 목표

Agent보다 먼저 Gemini 호출 자체를 검증한다.

구조:

```text
Prompt
 ↓
LLM Service
 ↓
Gemini
 ↓
Response
```

## 테스트 범위

```text
[ ] Text 호출
[ ] Structured Output
[ ] API Key 오류
[ ] Timeout
[ ] API 오류
```

개발 중에는 실제 응답을 Notebook에서 출력해 **모델 응답 형식이 예상과 맞는지 직접 확인**한다.

---

# 11. `07_skills.ipynb`

Skill은 한꺼번에 만들지 않고 하나씩 실행 검증한다.

권장 순서:

```text
Discovery
 ↓
Brand Strategy
 ↓
Customer
 ↓
Business
 ↓
Market
 ↓
Visual Direction
 ↓
Creative Asset
```

각 Skill은:

```text
Input
 ↓
Context
 ↓
Skill
 ↓
Structured Result
```

형태로 실행한다.

Skill 결과는 처음부터 바로 BrandState를 덮어쓰지 않는다.

```text
Skill
 ↓
Result
 ↓
Artifact
 ↓
Approval
 ↓
BrandState Mutation
```

---

# 12. `08_agent.ipynb`

## 목표

사용자 문장을 입력하면 Agent가 적절한 Skill/Tool을 선택하고 실행하는지 확인한다.

## 예시 1

입력:

```text
우리 브랜드의 타깃 고객을 정의해줘.
```

예상:

```text
Agent
 ↓
Router
 ↓
Customer Skill
 ↓
LLM
 ↓
Result
```

## 예시 2

```text
시장 규모를 조사해줘.
```

예상:

```text
Router
 ↓
Market / Research
```

## Notebook 로그

초기 개발에서는 내부 실행 과정을 최대한 보여준다.

```text
[USER]
시장 규모를 조사해줘.

[AGENT]
intent = MARKET_RESEARCH

[ROUTER]
tool = research

[RESEARCH]
query = ...

[RESULT]
sources = 8

[AGENT]
creating ResearchReport...
```

Notebook이 **개발자용 Agent 관찰 화면** 역할을 한다.

---

# 13. `09_tools.ipynb`

Tool은 Agent와 분리해서 먼저 단독 실행한다.

대상:

```text
Web Search
Research
Browser
Document
Image
Export
```

각 Tool에 대해:

```text
입력
 ↓
실행
 ↓
외부 결과
 ↓
정규화 결과
 ↓
오류 처리
```

를 확인한다.

---

# 14. `10_quick_research.ipynb`

## 목표

최소한의 Research Pipeline을 완성한다.

```text
Query
 ↓
Search
 ↓
Sources
 ↓
Summary
 ↓
Research Result
```

Notebook에서는 다음을 모두 출력한다.

```text
검색어
검색 결과 수
Source 목록
Source별 핵심 내용
최종 요약
```

---

# 15. `11_artifact.ipynb`

AI 결과물을 단순 문자열로 저장하지 않고 Artifact로 관리한다.

예:

```python
artifact = create_artifact(
    brand_id=brand.id,
    type="brand_strategy",
    title="Brand Strategy",
    content=result
)
```

상태 변화도 검증한다.

```text
draft
 ↓
approved
```

또는

```text
draft
 ↓
rejected
```

---

# 16. `12_asset.ipynb`

Asset은 DB metadata와 실제 파일을 분리한다.

```text
Asset Metadata
+
Actual File
```

Notebook에서:

```text
파일 생성
 ↓
Storage 저장
 ↓
DB metadata 저장
 ↓
조회
 ↓
실제 파일 존재 확인
```

---

# 17. `13_deep_research.ipynb`

Deep Research는 Backend 기반이 안정된 뒤 개발한다.

## 실행 흐름

```text
Research Request
 ↓
Research Plan
 ↓
Plan 출력
 ↓
Approve
 ↓
ResearchJob 생성
 ↓
검색/수집
 ↓
Normalize
 ↓
ResearchReport
 ↓
Findings
 ↓
Sources
```

## Job 상태 관찰

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

실패/취소도 확인한다.

```text
failed
cancelled
```

---

# 18. `14_export.ipynb`

최종 내부 데이터를 외부 문서로 출력한다.

```text
BrandState
+
Artifacts
+
Research
+
Assets
 ↓
Export
```

초기에는:

```text
JSON
 ↓
PDF
```

순서로 구현하고 DOCX 등은 후속 확장한다.

---

# 19. API를 Notebook에서도 검증한다

함수 호출만으로 끝내지 않는다.

FastAPI `TestClient`를 사용하여 Router까지 확인한다.

```python
from fastapi.testclient import TestClient

client = TestClient(app)

response = client.get("/health")
print(response.status_code)
print(response.json())
```

Brand API:

```python
response = client.post(
    "/brands",
    json={"name": "Notebook Brand"},
    headers=headers,
)

print(response.status_code)
print(response.json())
```

즉, 각 기능마다:

```text
Service 직접 호출
+
HTTP API 호출
```

두 가지를 모두 확인한다.

---

# 20. Notebook과 pytest의 역할 분리

Notebook은:

```text
탐색
개발
관찰
디버깅
```

pytest는:

```text
자동 회귀 테스트
```

에 사용한다.

개발 흐름:

```text
Notebook에서 처음 실행
 ↓
문제 발견
 ↓
Backend 수정
 ↓
Notebook 재실행
 ↓
정상 확인
 ↓
pytest 작성
```

---

# 21. 개발 데이터 분리

Notebook에서는 실제 서비스 데이터를 사용하지 않는다.

권장:

```text
TEST_USER
TEST_BRAND
TEST_CONVERSATION
TEST_ARTIFACT
TEST_RESEARCH
```

Development/Test DB를 Production DB와 분리한다.

```text
Notebook
 ↓
Development/Test DB
```

Production은:

```text
Frontend
 ↓
Backend
 ↓
Production DB
```

로 분리한다.

---

# 22. 최종 `99_backend_e2e.ipynb`

Backend Phase가 끝나면 하나의 Notebook에서 전체 흐름을 재현할 수 있어야 한다.

```text
1. Test User 생성
        ↓
2. Login
        ↓
3. Brand 생성
        ↓
4. BrandState 생성/조회
        ↓
5. Conversation 생성
        ↓
6. User Message 입력
        ↓
7. Agent 실행
        ↓
8. Skill 선택
        ↓
9. LLM 실행
        ↓
10. Artifact 생성
        ↓
11. BrandState 반영
        ↓
12. Research 실행
        ↓
13. Research 저장
        ↓
14. Asset 저장
        ↓
15. Export
```

이 Notebook은 **NAME TAG Backend의 최종 시연용 개발 콘솔**이 된다.

---

# 23. 최종 Backend 완료 조건

다음이 모두 가능하면 Frontend 개발을 시작한다.

```text
[ ] 회원가입
[ ] 로그인
[ ] Brand 생성/조회/수정/삭제
[ ] BrandState 저장/조회/수정
[ ] Conversation 저장/조회
[ ] LLM 호출
[ ] 최소 2개 Skill 실제 실행
[ ] Agent 기본 실행
[ ] Quick Research 실행
[ ] Artifact 생성/조회
[ ] Asset 저장/조회
[ ] Export 실행
[ ] API 테스트 통과
[ ] pytest 통과
[ ] 99_backend_e2e.ipynb 성공
```

---

# 24. Frontend 개발 시작 원칙

Frontend는 Backend를 설계하는 도구가 아니라 **이미 검증된 Backend를 사용하는 사용자 인터페이스**로 만든다.

즉:

```text
Backend Contract
 ↓
Swagger / Notebook 검증
 ↓
API 확정
 ↓
Frontend 연결
```

순서를 지킨다.

---

# 25. 최종 개발 철학

NAME TAG V2 초기 개발은 다음 한 문장으로 정의한다.

> **Notebook에서 백엔드를 먼저 만들고, 눈으로 확인하고, API로 확인하고, 테스트로 고정한 뒤 프론트를 만든다.**

특히 NAME TAG의 핵심인

```text
BrandState
+
Agent
+
Skill
+
Tool
+
Research
+
Artifact
```

는 서로 강하게 연결되므로, **프론트 화면보다 내부 데이터 흐름을 먼저 검증하는 방식**을 기본 개발 전략으로 사용한다.
