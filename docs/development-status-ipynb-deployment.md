# NAME TAG 개발 현황 및 IPYNB/배포 계획

작성 기준일: 2026-10-01

## 1. 현재 상태 요약

현재 저장소는 목표 아키텍처의 모델·서비스·스키마를 상당 부분 생성해 둔 초기 백엔드 골격이다. 실제 실행과 검증이 확인된 범위는 다음과 같다.

- FastAPI 앱과 `/health` 엔드포인트
- 세션 쿠키 기반 회원가입, 로그인, 현재 사용자 조회, 로그아웃
- Brand 생성 및 현재 사용자의 Brand 목록 조회
- BrandMember owner 생성
- BrandState 초기화 및 멤버십 검증을 포함한 조회
- Proposal/History 라우터와 관련 모델·서비스의 초기 구조
- SQLAlchemy와 Alembic 기반 SQLite 개발 DB
- React/Vite 프론트엔드의 화면·API 파일 골격

현재 코드에 파일은 있지만 실제 제품 흐름에 연결되지 않은 영역도 있다.

- Conversation, Agent, Research, Asset, Document, Export API는 앱 진입점에 아직 연결되지 않았다.
- BrandState는 현재 조회 API만 있고 부분 수정·버전 충돌 처리 API가 없다.
- Skill/Tool/LLM 코드는 존재하지만 API에서 끝까지 실행되는 검증이 없다.
- 테스트 디렉터리와 pytest 테스트가 없다.
- IPYNB는 이번 작업에서 `notebooks/00_backend_environment.ipynb`를 추가했다.
- `docker-compose.yml`은 비어 있고, `frontend/package.json`도 비어 있어 프론트엔드/배포 실행 계약이 아직 없다.

## 2. 이번 작업에서 확인한 사실

IPYNB에서 다음 흐름을 실제 실행했다.

```text
백엔드 경로 설정
  -> Alembic upgrade head
  -> 앱 모듈 재로드
  -> GET /health
  -> POST /api/auth/signup
  -> GET /api/auth/me
  -> POST /api/brands
  -> GET /api/brands
  -> GET /api/brands/{brand_id}/state
```

모두 통과했다. 이 과정에서 발견하고 수정한 문제는 다음과 같다.

- `backend/requirements.txt`에서 `argon2-cffi`와 `email-validator`가 붙어 있던 의존성 오류를 수정했다.
- SQLite 상대 경로 때문에 migration DB와 앱 DB가 달라지는 문제가 있었다. IPYNB에서 migration과 앱 import 전에 `backend/`를 작업 디렉터리로 고정하도록 만들었다.
- FastAPI 최신 버전의 nested router 표현을 고려해 노트북의 라우트 검사 로직을 수정했다.
- 노트북 셀이 이전 셀의 변수에 의존하지 않도록 핵심 실행 셀을 독립적으로 보정했다.

## 3. 현재 완료 판단

### 완료 또는 동작 확인

- [x] 앱 import
- [x] `/health`
- [x] 세션 쿠키 기반 signup/login/me/logout 코드
- [x] Brand 생성/목록 코드
- [x] BrandState 초기화/조회 코드
- [x] IPYNB에서 위 흐름 재현
- [x] Alembic migration 실행 확인

### 아직 완료로 볼 수 없는 것

- [ ] DB 경로와 환경변수 계약의 고정
- [ ] BrandState PATCH 및 부분 병합
- [ ] 사용자 간 Brand 접근 격리 자동 테스트
- [ ] Proposal 승인/적용 및 History mutation의 통합 흐름
- [ ] Conversation 저장/조회 API 연결
- [ ] Agent API와 Skill 실행
- [ ] Quick Research와 결과 저장
- [ ] Asset/Document/Export 실행
- [ ] pytest 회귀 테스트
- [ ] 프론트엔드 npm 실행 계약
- [ ] Docker Compose 및 staging 배포

## 4. IPYNB 개발 순서

각 노트북은 다음 순서를 지킨다.

```text
환경 준비
  -> migration
  -> 앱/서비스 import
  -> 정상 케이스
  -> DB 재조회
  -> 실패/권한 케이스
  -> HTTP API 확인
  -> pytest로 고정
```

권장 노트북 순서:

1. `00_backend_environment.ipynb`: 앱 import, migration, health, 기본 API
2. `01_auth_and_brand.ipynb`: signup/login/me/logout, Brand 격리
3. `02_brand_state.ipynb`: 초기화, 부분 수정, version, 잘못된 Brand 접근
4. `03_proposal_history.ipynb`: propose, approve, apply, snapshot, history
5. `04_conversation.ipynb`: conversation/message 저장 및 재조회
6. `05_llm_and_skills.ipynb`: mock LLM부터 Discovery/Brand Strategy 실행
7. `06_agent.ipynb`: 자연어 입력, router, skill, artifact 응답
8. `07_quick_research.ipynb`: source, report, finding 저장
9. `08_asset_document_export.ipynb`: 파일 metadata, document block, export
10. `99_backend_e2e.ipynb`: 회원가입부터 export까지 전체 시나리오

외부 LLM과 웹 검색은 비용과 변동성이 있으므로 기본 노트북은 mock provider로 통과시키고, 별도의 live 노트북에서 실제 Gemini 키가 있을 때만 실행한다.

## 5. 구현 우선순위

### P0: 실행 기반 고정

- `DATABASE_URL`을 환경변수로 명시하고 SQLite 경로를 절대 경로 또는 프로젝트 기준 경로로 통일한다.
- `docker-compose.yml`을 backend, frontend, database 개발 실행 계약으로 채운다.
- Alembic migration의 head와 모델 import 범위를 정리한다.
- `BrandState PATCH`와 부분 병합, version 증가, optimistic locking을 구현한다.
- `backend/tests`와 공통 TestClient/임시 SQLite fixture를 추가한다.

### P1: 서버 핵심 흐름

- 인증/Brand 접근 격리 테스트
- BrandState mutation -> Proposal -> Approval -> Snapshot -> History
- Conversation/Message API
- Artifact 저장과 승인 상태
- Agent 라우터를 앱에 연결하되 LLM은 mock 가능한 Gateway로 둔다.

### P2: Research와 Workspace

- Quick Research source/report/finding 저장
- Research 결과를 자동으로 BrandState에 쓰지 않고 Proposal로 연결
- Asset metadata와 파일 저장소 추상화
- Document/Block API
- PDF/Brand Kit export

### P3: 프론트엔드 연결

- 비어 있는 `frontend/package.json`과 Vite 실행 계약 복구
- API client, auth, Brand dashboard, Workspace route 연결
- TanStack Query 서버 상태와 Zustand UI 상태 분리
- 로그인/Brand 전환/로그아웃 시 query cache 격리

### P4: 배포 전 운영 강화

- PostgreSQL staging migration
- object storage 연결
- secure cookie, CORS, CSRF, rate limit, secret 관리
- usage/audit 로그
- Playwright 핵심 E2E
- health/readiness endpoint와 로그/모니터링

## 6. 배포 전략

### 개발

```text
VS Code / IPYNB
  -> SQLite
  -> FastAPI TestClient
  -> mock LLM/research provider
```

### Staging

```text
Frontend static build
  -> static hosting
FastAPI
  -> managed container service
PostgreSQL
  -> managed database
Assets
  -> S3/R2/Supabase Storage
Secrets
  -> hosting secret manager
```

### Production 전환 조건

다음이 모두 통과해야 배포한다.

- `alembic upgrade head`가 빈 DB에서 성공
- pytest 전체 통과
- User A가 User B Brand/Research/Document를 조회할 수 없음
- viewer가 mutation을 실행할 수 없음
- 서버 재시작 후 핵심 데이터가 유지됨
- LLM 없이 mock E2E가 통과
- staging에서 실제 Gemini 호출 1회와 비용/실패 로그 확인
- frontend build와 backend health check 통과
- secret이 코드·노트북·localStorage에 저장되지 않음

## 7. 다음 직접 작업 순서

1. DB 경로와 migration을 고정한다.
2. `01_auth_and_brand.ipynb`와 권한 pytest를 만든다.
3. BrandState PATCH/Proposal/History를 API까지 연결한다.
4. Conversation과 Artifact를 API에 연결한다.
5. mock 기반 Agent E2E를 통과시킨다.
6. Quick Research를 저장 가능한 형태로 만든다.
7. Docker Compose와 frontend 실행 계약을 복구한다.
8. staging 배포 후 Playwright로 로그인부터 Workspace까지 검증한다.

현재는 Deep Research나 복잡한 UI보다, IPYNB에서 매번 재현 가능한 backend 계약과 사용자 데이터 격리를 먼저 완료해야 한다.
