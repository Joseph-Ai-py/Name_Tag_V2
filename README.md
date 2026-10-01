# NAME TAG V2

NAME TAG는 사용자의 사업과 브랜드를 하나의 지속적인 Workspace로 관리하는 AI Brand Workspace입니다.

현재 개발은 Backend-first 방식으로 진행되고 있습니다.

```text
Backend Function
	-> API
	-> Database Persistence
	-> Swagger / pytest 검증
	-> Frontend 연결
```

## 현재 구현 범위

### 인증과 Brand

- 이메일/비밀번호 회원가입 및 로그인
- HttpOnly 세션 쿠키 기반 인증
- 로그아웃 및 현재 사용자 조회
- Brand 생성·조회·수정·삭제
- `owner`, `editor`, `viewer` 기본 권한
- 사용자별 Brand 데이터 격리

### Brand Workspace 데이터

- BrandState 단일 저장소
- 부분 수정 및 version 충돌 검사
- Conversation / Message 저장
- Artifact 생성 및 승인·거절
- Proposal 승인·적용
- Snapshot / History 기록

### Agent와 LLM

- 메시지 의도 분류 Router
- BrandState Context Manager
- Skill Registry / Executor
- Tool Registry와 role 기반 Tool permission
- Mock LLM Gateway
- Gemini Gateway
- 구조화된 Gemini JSON 응답 및 Artifact 정규화

### Research

- Quick Research Job / Report / Source / Finding
- Deep Research Plan 및 Job lifecycle
- `planning -> approved -> cancelled` 상태 흐름
- Finding을 Proposal로 연결
- Brand 멤버십 기반 Research 접근 제어
- Research UsageEvent 기록

### Workspace와 Export

- Asset metadata CRUD
- Block 기반 Document / Block CRUD
- BrandState·Artifact·Asset·Research를 포함하는 JSON Export

현재 최신 Alembic head는 `9f2a8b3c4d5e`입니다.

## 아직 구현 중인 범위

- 실제 Web Search provider 연결
- Deep Research background worker 실행
- PDF / Brand Kit export
- Object Storage 실제 파일 업로드
- Email verification, password reset, rate limit, CSRF hardening
- Frontend React/Vite 실제 화면 연결
- 고급 Skill별 도메인 실행 로직

현재 `frontend/`는 구조와 파일명 중심의 scaffold 상태이므로, Backend API를 먼저 검증합니다.

## Frontend 실행

Frontend는 React + TypeScript + Vite로 구성되어 있습니다.

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

브라우저에서 `http://localhost:5173/`을 엽니다.

- Backend가 실행 중이면 로그인 후 실제 Brand와 Agent API를 사용합니다.
- `Demo Workspace 열기`를 누르면 Backend 없이 화면과 Workspace 흐름을 확인할 수 있습니다.
- Vite 개발 서버의 `/api` 요청은 `http://127.0.0.1:8000`으로 proxy됩니다.

Frontend 검증:

```bash
cd frontend
npm run build
npm test -- --passWithNoTests
```

현재 Frontend는 실제 로그인·BrandState·Agent Chat 연결과 Demo Workspace를 제공하며, Research/Asset/Document 화면은 Workspace shell에서 다음 연결 단계로 확장할 수 있습니다.

## 개발 환경 설정

Backend는 Python 3.11 이상이 필요합니다.

```bash
cd backend
python -m pip install -r requirements.txt
```

환경변수 파일을 생성합니다.

```bash
cp ../.env.example .env
```

기본 설정은 외부 API를 호출하지 않는 Mock LLM입니다.

```env
LLM_PROVIDER=mock
```

Gemini를 사용하려면 새로 발급한 키를 로컬 `backend/.env`에 설정합니다.

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-new-key
GEMINI_MODEL=gemini-3-flash-preview
```

실제 API 키는 README, `.env.example`, Git 저장소에 기록하지 않습니다. 이전에 채팅이나 다른 곳에 노출된 키는 폐기하고 재발급해야 합니다.

## Database Migration

Backend 디렉터리에서 실행합니다.

```bash
cd backend
alembic upgrade head
```

현재 개발 기본 DB는 SQLite입니다. 설정은 `DATABASE_URL`로 변경할 수 있습니다.

```env
DATABASE_URL=sqlite:///./name_tag.db
```

Migration 상태 확인:

```bash
alembic heads
alembic current
```

## 서버 실행

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

확인할 주소:

- Health: `http://127.0.0.1:8000/health`
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`

## pytest 실행

전체 Backend 테스트:

```bash
cd backend
pytest -q
```

현재 기준 결과:

```text
24 passed
```

주요 테스트 파일:

- `tests/test_agent.py`: Agent, Conversation, Artifact
- `tests/test_llm_gateway.py`: Gemini Gateway 계약과 JSON 파싱
- `tests/test_skill_registry.py`: Skill Registry / Executor
- `tests/test_research.py`: Quick/Deep Research와 Proposal 연결
- `tests/test_assets_documents.py`: Asset / Document / Block
- `tests/test_export.py`: JSON Export
- `tests/test_tool_registry.py`: Tool Registry / Permission

## Swagger 테스트 순서

서버를 실행한 뒤 `/docs`에서 다음 순서로 테스트할 수 있습니다.

1. `POST /api/auth/signup`
2. `POST /api/auth/login`
3. `GET /api/auth/me`
4. `POST /api/brands`
5. `GET /api/brands/{brand_id}/state`
6. `PATCH /api/brands/{brand_id}/state`
7. `POST /api/brands/{brand_id}/conversations`
8. `POST /api/agent/chat`
9. `POST /api/research/quick`
10. `POST /api/research/plan`
11. `POST /api/research/jobs`
12. `POST /api/brands/{brand_id}/documents`
13. `POST /api/brands/{brand_id}/assets`
14. `POST /api/brands/{brand_id}/export`

## curl 예시

세션 쿠키를 파일에 저장해 인증 요청에 재사용합니다.

```bash
cd backend

curl -i -c /tmp/name-tag.cookies \
	-H 'Content-Type: application/json' \
	-d '{"email":"test@example.com","password":"Password123!"}' \
	http://127.0.0.1:8000/api/auth/signup

curl -i -b /tmp/name-tag.cookies \
	http://127.0.0.1:8000/api/auth/me

curl -i -b /tmp/name-tag.cookies -c /tmp/name-tag.cookies \
	-H 'Content-Type: application/json' \
	-d '{"name":"My Brand","description":"AI Brand Workspace"}' \
	http://127.0.0.1:8000/api/brands
```

`signup`을 이미 실행한 이메일이면 `login`을 사용합니다.

```bash
curl -i -b /tmp/name-tag.cookies -c /tmp/name-tag.cookies \
	-H 'Content-Type: application/json' \
	-d '{"email":"test@example.com","password":"Password123!"}' \
	http://127.0.0.1:8000/api/auth/login
```

## 기본 아키텍처

```text
Authenticated User
				|
				v
Brand Membership / Role
				|
				v
AI Consultant API
				|
				v
Agent Router
				|
				v
Skill Registry -> Skill Executor -> LLM Gateway
				|
				+-> Artifact / Proposal / Research
				|
				v
BrandState + Workspace + History
```

중요한 BrandState 변경은 바로 덮어쓰지 않고 다음 흐름을 사용합니다.

```text
Proposal -> Approval -> Snapshot -> Mutation -> History
```

Research Finding도 자동으로 BrandState에 적용하지 않고 Proposal로 연결합니다.