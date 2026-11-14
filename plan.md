# NAME TAG — Product Scope & Implementation Plan

> 상태: **DRAFT — 사용자 검토 및 승인 전**  
> 작성일: 2026-11-14  
> 기준 저장소: `Joseph-Ai-py/Name_Tag_V2`  
> 기준 브랜치: `docs/name-tag-product-scope-2026-11-14`  
> 관련 조사: [research.md](./research.md)

## 0. 이번 계획의 목적

세 저장소의 기능을 한 번에 합치거나 V2의 모든 모듈을 완성하는 것이 목표가 아니다.

**첫 번째로 완성할 제품은 “초기 아이디어 입력 → 브랜드 전략 생성 → 사용자 검토/확정 → 시각 결과물 생성 → 브랜드 가이드 PDF 출력 → 이후 지속 관리”가 끊기지 않는 AI Brand Workspace다.**

구현 범위는 다음 원칙을 따른다.

1. 이미 V2에 있는 인증, 브랜드별 데이터 격리, BrandState, Proposal, Snapshot, History, Conversation은 재사용한다.
2. Streamlit/초기 Name_Tag에서 실제 사용자 가치가 확인된 브랜드 인터뷰, 후보 믹스앤매치, Brand DNA, 이미지/PDF 결과물은 필요한 부분만 이식한다.
3. AI가 확정 BrandState를 직접 수정하지 못하게 한다.
4. 첫 릴리스에 필요하지 않은 인프라/에이전트 기능은 숨기거나 연기한다.
5. 구현 전 이 문서의 결정 사항을 사용자가 검토하고 승인한다.

## 1. 제품 목표와 성공 기준

### 제품 약속

“아이디어만 있는 사람도 AI와 함께 브랜드의 핵심 전략과 시각 정체성을 만들고, 그 결과를 하나의 Workspace에서 계속 개선하며, 실제로 사용할 수 있는 브랜드 가이드로 내보낼 수 있다.”

### 첫 릴리스의 완료 조건

아래 시나리오를 처음 가입한 사용자가 도움말 없이 완료할 수 있어야 한다.

1. 회원가입 후 새 Brand를 만든다.
2. 업종/서비스, 타겟, 감성, 키워드를 입력하고 인터뷰를 진행하거나 건너뛴다.
3. AI가 브랜드 후보를 만들고 사용자가 이름·의미·슬로건·스토리·대표 컬러를 조합해 확정한다.
4. 확정 내용이 BrandState에 저장되고 Workspace의 Business, Customer, Market, Brand, Visual 영역에서 확인된다.
5. 채팅으로 “타겟 고객을 더 구체화해줘” 또는 “브랜드 포지셔닝을 개선해줘”라고 요청하면 현재 BrandState를 반영한 결과가 생성된다.
6. AI 결과가 Artifact/Proposal로 표시된다. 사용자가 승인하기 전에는 BrandState가 바뀌지 않는다.
7. 사용자가 제안을 승인하면 BrandState 버전이 올라가고 Snapshot/History가 남는다. 거절하면 현재 BrandState는 유지된다.
8. 로고를 생성해 Asset으로 보관하고 Workspace에서 확인한다.
9. Brand DNA 및 출력 무결성 검사를 통과한 PDF 브랜드 가이드를 내려받는다.
10. 이전 Snapshot을 선택하면 그 시점의 브랜드 상태를 복원할 수 있다.

**이 10개가 동작하면 첫 제품의 핵심 가치는 전달된다.** Deep Research, AI Employee 회의, 블록 편집기, MCP 등이 없어도 된다.

## 2. 기능 범위 결정

### P0 — 첫 릴리스 필수

| ID | 기능 | 범위 | 완료 기준 |
| --- | --- | --- | --- |
| P0-01 | 인증 및 Brand 격리 | 회원가입/로그인/로그아웃, 사용자별 Brand 접근 제어 | 다른 사용자의 Brand/Asset/Conversation/Proposal에 접근 불가 |
| P0-02 | Brand 생성 및 초기 입력 | Brand 생성, 업종/서비스/타겟/감성/키워드 입력 | 생성한 Brand에 초기 BrandState가 연결됨 |
| P0-03 | Discovery 인터뷰 | 질문 생성, 답변 저장, 인터뷰 건너뛰기 | 답변과 기본 입력을 후보 생성 컨텍스트로 사용 |
| P0-04 | 브랜드 후보/믹스앤매치 | 후보 생성, 이름·의미·슬로건·스토리·컬러 필드별 선택 | 선택 결과가 사용자의 확인 후 BrandState에 저장 |
| P0-05 | Brand Workspace | Business/Market/Customer/Brand/Visual 정보 읽기·직접 수정 | 새로고침/재로그인 후에도 값 유지 |
| P0-06 | AI Consultant | 브랜드별 대화 기록, 맥락 조회, 핵심 도메인 작업 실행 | 현재 BrandState를 바탕으로 결과와 근거를 제공 |
| P0-07 | Artifact/Proposal 검토 | 초안 보기, 변경 전후 비교, 승인/거절/적용 | AI의 상태 변경은 승인 전 적용되지 않음 |
| P0-08 | Snapshot/History | 주요 변경 전 상태 저장, 이력 조회, 복원 | 충돌 처리와 복원 테스트 통과 |
| P0-09 | Visual Asset | 우선 로고 생성 및 실제 파일 업로드/저장/미리보기 | 파일 실체와 Asset metadata가 함께 유지됨 |
| P0-10 | Brand Kit PDF | BrandState + Asset 기반 HTML/PDF 생성 | 확정 브랜드명/현재 Brand DNA 기준 검증 후 정상 다운로드 |
| P0-11 | 품질 검증 | Backend unit/integration, frontend build, 핵심 E2E | 새 기능 회귀 테스트 통과, 기존 기능 회귀 없음 |

### P1 — 첫 릴리스 다음

- URL/문서 등 출처를 저장하는 Quick Research와 근거가 표시되는 Findings.
- Deep Research의 내구성 있는 background worker, 재시도, 진행 상태, 실패 복구.
- 캐릭터 이미지 생성과 캐릭터 가이드.
- 팀 협업 초대 및 owner/editor/viewer 세분화.
- PDF 외에 편집 가능한 문서/블록 편집기.
- 사용량·비용 분석 및 관리자 도구.

### P2 — 당장 만들지 않음

- AI Employee 여러 명이 토론하는 Meeting 기능.
- RAG/벡터 검색, Redis, SSE, MCP, 다중 모델 오케스트레이션.
- 여러 단계의 자율 에이전트 루프와 복잡한 Dependency Engine.
- 고급 자동화/대량 생성 기능.

### 지금 삭제하지 않을 것

- 기존 Meeting/Research/Document 모듈과 관련 DB/데이터를 이번 범위 축소만으로 삭제하지 않는다.
- 아직 데이터가 들어 있을 수 있는 SQLite DB, 업로드 파일, 사용자가 만든 Asset/Document는 별도 백업 및 데이터 확인 전 삭제하지 않는다.
- P1/P2 기능은 우선 UI/기본 동선에서 비활성 또는 미노출 처리하고, 별도 마이그레이션 계획 없이 DB 구조를 제거하지 않는다.

## 3. 도메인/데이터 설계 원칙

### 3.1 단일 기준 데이터

BrandState를 브랜드의 정규 데이터 원천으로 유지한다. 같은 값을 프론트엔드 임시 상태, Artifact, 별도 테이블에 각각 “확정값”으로 저장하지 않는다.

| 영역 | 주요 필드 예시 | 사용 목적 |
| --- | --- | --- |
| Business | industry, service, problem, solution, business_model, pricing | 사업과 제공 가치 |
| Market | competitors, trends, market_size, swot, evidence_refs | 시장/경쟁 환경 |
| Customer | target, segments, persona, needs, pain_points, journey, jtbd | 고객 이해 |
| Brand | name, meaning, mission, vision, values, positioning, story, personality, tone, tagline | 브랜드 전략 |
| Visual | colors, typography, mood, design_principles, logo_asset_id | 시각 정체성 |

- 위 필드는 초기 제안이다. 구현 전에 기존 `canonical_section_extensions()`, `ALLOWED_PATHS`, Schema, Migration을 대조해 최종 확정한다.
- Legacy O/A/B/C/DE의 상세 JSON 출력 전체를 BrandState에 무차별 삽입하지 않는다. 세부 분석/응답/선택지는 Artifact로 보존하고, Workspace에서 운영할 요약·확정 필드만 BrandState에 저장한다.
- 필드명/타입/nullable/배열 여부를 문서화하고, Pydantic 검증과 변경 허용 경로를 일치시킨다.
- 기존 사용자 데이터가 있다면 JSON 구조를 바로 바꾸지 않는다. 데이터 샘플을 확인하고 명시적 Migration/Adapter를 만든다.

### 3.2 데이터 객체의 책임

- **Conversation/Message:** 사용자의 질문과 AI 응답의 대화 기록.
- **Artifact:** 생성된 분석/브랜드 초안/가이드 콘텐츠. 제안과 구별되며, 사용자가 다시 열어볼 수 있다.
- **Proposal:** BrandState에 적용할 변경 집합과 변경 요약. 생성 시 기준 버전을 기록한다.
- **Snapshot:** 변경 직전의 BrandState 전체 복사본.
- **History:** 누가 언제 무엇을 변경/승인/복원했는지 기록.
- **Asset:** 로고 이미지 등 실제 파일을 가리키는 메타데이터. 파일 저장소와 실제 파일이 일치해야 한다.
- **Research Report/Source/Finding:** 조사 근거를 보존한다. Finding은 사용자 승인 없이 BrandState에 직접 반영하지 않는다.

### 3.3 변경 처리 규칙

AI가 만든 BrandState 변경은 아래 경로를 사용한다.

```text
User Request
  -> Agent + Brand Context
  -> Artifact / Proposal Draft
  -> User Review
  -> Approve or Reject
  -> Version Check
  -> Snapshot
  -> BrandState Mutation
  -> History
```

- Proposal의 기준 버전이 현재 버전과 다르면 덮어쓰지 말고 409 충돌로 반환한다.
- 사용자가 직접 수정하는 경우에도 허용 필드 검증, 예상 버전 확인, Snapshot/History를 적용한다.
- AI에게 사용자 역할을 우회하는 Tool을 제공하지 않는다.
- PDF/Asset 생성 실패는 BrandState 변경 성공으로 처리하지 않는다.

## 4. 구현 순서 및 파일 단위 계획

### Stage 0 — 구현 전 계약 확정

**목표:** 기능 중복과 잘못된 데이터 모델을 먼저 제거한다. 이 단계에서는 코드 동작을 변경하지 않는다.

대상:
- `research.md`
- `docs/architecture/overview.md`
- `docs/legacy-skill-migration.md`
- `backend/app/services/brand_state_service.py`
- `backend/app/services/mutation_service.py`
- `backend/app/core/legacy_template.py`
- `backend/app/schemas/brand_state.py`
- `backend/app/alembic/versions/`

작업:
1. 현재 BrandState의 실제 초기 구조와 허용 변경 경로를 표로 추출한다.
2. Legacy O/A/B/C/DE 각 필드를 새 영역에 매핑한다.
3. BrandState에 남길 필드와 Artifact에만 남길 필드를 구분한다.
4. 현재 사용 데이터/DB의 존재 여부를 확인하고 데이터 마이그레이션 필요 여부를 판단한다.
5. 최종 API 계약과 Proposal 상태 전이를 문서화한다.

**완료 기준:** 필드 중복·잘못된 경로·기존 데이터 손실 가능성에 대한 미해결 항목이 없다.

### Stage 1 — Discovery 및 초기 브랜드 생성

**주요 레거시 참고**
- `Name_Tag_Streamlit/logic_o.py`
- `Name_Tag_Streamlit/models.py`
- `Name_Tag/backend/routers/section_o.py`
- `Name_Tag/frontend/src/pages/SectionO.tsx`
- V2 `backend/app/skills/registry.py`

**V2 변경 후보**
- `backend/app/skills/registry.py`
- `backend/app/skills/executor.py`
- `backend/app/skills/domain.py`
- `backend/app/llm/schemas.py`
- `backend/app/api/agent.py` 또는 Discovery 전용 API
- `backend/app/services/brand_state_service.py`
- `frontend/src/app/App.tsx` (현재 실제 UI 집중 위치)

작업:
1. 초기 입력 필드와 Discovery 인터뷰 계약을 확정한다.
2. 답변을 저장하고 인터뷰 건너뛰기 동선을 지원한다.
3. 후보는 4개 기준으로 생성하되 실제 응답 스키마로 개수/필드를 검증한다.
4. 사용자는 이름/의미/슬로건/스토리/대표 컬러를 각각 선택할 수 있다.
5. 최종 선택은 사용자 확인 후 BrandState에 반영한다. 필요 시 Proposal 흐름을 그대로 사용한다.
6. 후보 수·각 필수 필드 누락·Gemini JSON 파싱 실패·재생성 오류를 테스트한다.

**완료 기준:** 처음 생성한 Brand가 Workspace에 표시되고, 새로고침 이후 선택 내용이 보존된다.

### Stage 2 — Workspace 데이터 표시와 직접 편집

대상:
- `frontend/src/app/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/hooks/useBrandState.ts`
- `backend/app/api/brand_state.py`
- `backend/app/services/brand_state_service.py`
- `backend/app/services/mutation_service.py`

작업:
1. Workspace 영역을 Business, Market, Customer, Brand, Visual로 정리한다.
2. 확정 BrandState와 생성 Artifact를 시각적으로 구분한다.
3. 필드별 직접 편집 및 저장을 지원한다.
4. 모든 변경에서 예상 버전과 허용 경로를 검사한다.
5. `App.tsx`에서 기능별 빈 파일로 코드를 무작정 이동하지 않는다. API/상태 계약을 먼저 안정화하고 실제 기능 단위로 필요한 모듈만 분리한다.

**완료 기준:** 브랜드 정보가 유실되지 않고 조회/수정되며, 다른 브랜드나 사용자의 데이터가 섞이지 않는다.

### Stage 3 — AI Consultant와 Artifact/Proposal UX

대상:
- `backend/app/agent/core.py`
- `backend/app/agent/router.py`
- `backend/app/agent/context_manager.py`
- `backend/app/agent/planner.py`
- `backend/app/skills/registry.py`
- `backend/app/skills/executor.py`
- `backend/app/services/agent_service.py`
- `backend/app/services/artifact_service.py`
- `backend/app/services/proposal_service.py`
- `backend/app/api/agent.py`
- `backend/app/api/proposals.py`
- `frontend/src/app/App.tsx`

작업:
1. MVP에서 쓸 Skill을 Discovery, Business, Market, Customer, Brand Strategy, Visual로 제한한다.
2. 대화에는 해당 BrandState와 최근 Conversation을 컨텍스트로 제공한다.
3. 일반 설명 요청은 답변/Artifact로, 확정 데이터 변경 요청은 Proposal로 반환한다.
4. Proposal 카드에 변경 전/후, 이유, 기준 버전을 표시한다.
5. 승인/거절 버튼과 로딩/오류 상태를 명확히 한다.
6. Agent의 계획/Tool 호출은 최대 반복·호출 예산, 권한 검사, 구조화된 출력 검증을 유지하되, 불필요한 자율 반복은 줄인다.

**완료 기준:** Agent 요청 후 승인 전 BrandState는 변하지 않고, 승인된 변경만 한 번 적용된다.

### Stage 4 — Snapshot/History 안전성 검증

대상:
- `backend/app/services/proposal_service.py`
- `backend/app/services/brand_state_service.py`
- `backend/app/services/snapshot_service.py`
- `backend/app/services/history_service.py`
- `backend/app/api/history.py`
- 관련 `backend/tests/test_*.py`

작업:
1. Proposal 적용, 직접 편집, 복원 모두에 대해 스냅샷 생성 규칙을 통일한다.
2. 중복 적용, 이미 처리된 Proposal, 버전 불일치, 동시 업데이트를 테스트한다.
3. Snapshot 복원도 새 버전으로 기록하고 History를 남긴다.
4. 복원 대상과 현재 상태를 사용자에게 분명히 보여준다.

**완료 기준:** 변경/복원으로 데이터가 조용히 덮어써지지 않고 모든 상태 전이가 추적된다.

### Stage 5 — 실제 파일 Asset 및 PDF Brand Kit

**주요 레거시 참고**
- `Name_Tag_Streamlit/logic_de.py`
- `Name_Tag_Streamlit/brand_dna.py`
- `Name_Tag_Streamlit/pdf_builder.py`
- `Name_Tag_Streamlit/pdf_service.py`
- `Name_Tag/backend/services/image_service.py`
- `Name_Tag/backend/pdf/nametag_pdf_builder.py`

**V2 변경 후보**
- `backend/app/models/asset.py`
- `backend/app/services/asset_service.py`
- `backend/app/api/assets.py`
- `backend/app/llm/gateway.py`
- `backend/app/config.py`
- 신규 image provider adapter
- 신규 Brand DNA mapper/integrity validator
- 신규 PDF builder/service
- `backend/app/services/export_service.py`
- `backend/app/api/export.py`
- `frontend/src/app/App.tsx`

작업:
1. 로컬 개발과 운영 환경에서 실제 파일을 저장할 경로/스토리지 인터페이스를 결정한다.
2. 로고 이미지 생성 API를 adapter로 연결하고 생성 실패/재시도/비용을 처리한다.
3. 업로드/생성된 이미지 파일의 실제 존재와 MIME type, 크기를 검증한다.
4. Asset metadata와 실제 파일을 하나의 lifecycle로 관리한다.
5. BrandState와 Asset으로 Brand DNA를 만들고, 브랜드 이름/타 브랜드 샘플 문구 오염 여부를 검사한다.
6. 기존 PDF 디자인을 참고해 HTML을 조립하고 PDF로 출력한다.
7. PDF 직전 최종 결과를 검사하고 실패하면 다운로드를 막는다.
8. JSON Export는 백업/이전 기능으로 남기되, 사용자에게 보여줄 최종 결과물은 PDF Brand Kit으로 구분한다.

**완료 기준:** 로고가 파일로 보존되고, 이미지가 포함된 PDF가 정확한 브랜드 정보로 생성되며, 무결성 실패 시 파일을 제공하지 않는다.

### Stage 6 — 회귀 테스트 및 릴리스 점검

검증 명령(실제 의존성과 설정을 확인한 후 실행):
- Backend: `cd backend && pytest -q`
- Frontend: `cd frontend && npm run build`
- Frontend tests: `cd frontend && npm test`
- E2E: Playwright 시나리오 추가 후 실행
- Local run: Backend + Frontend + 테스트 계정 + Gemini 키로 end-to-end 실행

필수 시나리오:
- 신규 회원 → Brand 생성 → 인터뷰/건너뛰기 → 후보 선택 → BrandState 저장
- Agent chat → Artifact/Proposal 생성 → 승인 전 상태 불변 → 승인 후 변경
- Proposal 거절 → 상태 불변
- 오래된 Proposal 적용 → 409 충돌
- Snapshot 복원 → 새로운 버전 및 History 생성
- 사용자 A가 사용자 B의 Brand/Asset/Conversation/Research에 접근 불가
- 로고 생성/업로드 → Asset 조회 → PDF에 이미지 포함
- 브랜드 이름 누락/타 브랜드 오염 문구 → PDF 생성 차단
- LLM 응답 오류/JSON 파싱 오류/파일 저장 실패 → 사용자에게 복구 가능한 오류 표시

## 5. 저장소 정리 작업 — 기능 구현과 분리

아래 항목은 제품 기능 작업과 별도 커밋으로 다룬다.

- `__pycache__`와 `.pyc`가 Git 추적 대상에서 제외되는지 확인하고 .gitignore를 보강한다.
- 추적 중인 SQLite DB 2개의 실제 용도를 확인한다. 데이터가 필요한 경우 백업/fixture 분리 후에만 추적 해제한다.
- 0바이트 파일은 참조 여부를 검색한 뒤 실제로 쓰이지 않는 파일만 정리한다. 무조건 일괄 삭제하지 않는다.
- 비어 있는 API/architecture 문서를 실제 구현과 일치하게 채운다.
- 루트 README의 기능/실행/미완성 상태를 코드와 테스트 결과에 맞게 갱신한다.
- 실제 실행하지 않은 테스트를 “통과”라고 기록하지 않는다.

## 6. 위험 요소와 대응

| 위험 | 영향 | 대응 |
| --- | --- | --- |
| Legacy 필드와 V2 BrandState가 불일치 | 기존 결과/데이터 손실 | Stage 0에서 매핑표와 Migration 검토 |
| AI가 확인되지 않은 내용을 사실처럼 생성 | 브랜드 전략 오류 | 근거/가설 구분, Artifact 미리보기, 사용자 승인 |
| Proposal 적용 시 버전 충돌 | 최근 사용자 수정 덮어쓰기 | base version 검사와 409 처리 |
| Asset metadata만 저장되고 파일이 없음 | 로고/PDF 깨짐 | 실제 파일 존재 검증과 storage adapter |
| PDF 렌더러/폰트/이미지 경로 오류 | 최종 산출물 실패 | 고정된 렌더링 환경과 PDF E2E 테스트 |
| 기능을 한꺼번에 이식 | 코드 복잡도 증가 | P0 단계별 병합, 각 단계 테스트 |
| SQLite/pycache 정리 중 데이터 손실 | 저장 데이터 손실 | 백업 및 추적 파일 용도 확인 후 처리 |

## 7. 이번 범위에서 제외할 구현

- AI Employee/Meeting 기능 신규 개발 또는 개선
- Deep Research 운영용 worker와 외부 검색 provider 구축
- RAG/Redis/SSE/MCP/멀티모델 시스템 도입
- 전체 Block Editor 고도화
- 캐릭터 생성의 고급 편집기
- 전면적인 프론트엔드 재작성
- 세 저장소의 코드/데이터를 일괄 복사하거나 삭제하는 작업

## 8. 진행 상태 체크리스트

- [x] 세 저장소 README 및 주요 구조 조사
- [x] 핵심 서비스/API/모델/테스트 정적 조사
- [x] 기준 저장소를 `Name_Tag_V2`로 제안
- [x] 핵심 기능과 P1/P2 범위 구분
- [x] 연구 문서 작성
- [x] 구현 계획 초안 작성
- [ ] 사용자의 인라인 검토/주석 반영
- [ ] 계획 최종 승인
- [ ] Stage 0 상세 설계 완료
- [ ] P0 구현 시작
- [ ] P0 회귀 및 E2E 검증 완료

## 9. 사용자 주석 반영 방식

이 문서의 해당 항목 바로 아래에 아래 형식으로 의견을 남겨 주세요.

```md
> [USER NOTE]
> 변경/추가/삭제할 내용:
> 이유:
```

주석을 받으면 다음 단계는 **계획 문서만 수정**하는 것이다. 사용자의 추가 지시가 명시적으로 구현 승인으로 이어지지 않는 한 코드 구현은 시작하지 않는다.

## 10. 구현 승인 후 사용할 표준 실행 규칙

- 승인된 계획과 범위 밖의 파일은 수정하지 않는다.
- 작업을 시작하기 전 해당 파일과 호출 경로를 다시 읽는다.
- 단계별 작업을 하나씩 구현하고 완료 즉시 이 체크리스트를 갱신한다.
- 수정 전후 테스트를 실행하고 새로운 오류가 생기면 원인을 먼저 확인한다.
- `unknown` 타입/검증 없는 임의 JSON 변경을 피하고, Pydantic/TypeScript 계약을 일치시킨다.
- 각 기능 완료 시 단위 테스트와 연관 통합 테스트를 실행한다.
- 구현 접근이 잘못된 경우 기존 패치 위에 임시 수정만 쌓지 않는다. Git diff를 확인하고 안전하게 이전 상태로 되돌린 뒤 더 작은 범위로 다시 계획한다.
- 모든 단계가 완료되기 전 임의로 다음 기능을 추가하지 않는다.

---

## 승인 게이트

**현재 상태는 계획 초안이다.** 사용자가 이 문서의 방향과 우선순위를 검토한 뒤 승인하기 전까지 기능 코드, DB migration, 프론트 UI, API 동작은 수정하지 않는다.
