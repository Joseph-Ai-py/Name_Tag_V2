# NAME TAG — Codebase Research

> 조사 기준일: 2026-11-14 (Asia/Seoul)  
> 조사 대상: `Joseph-Ai-py/Name_Tag_Streamlit`, `Joseph-Ai-py/Name_Tag`, `Joseph-Ai-py/Name_Tag_V2`  
> 기준 저장소 제안: `Joseph-Ai-py/Name_Tag_V2`  
> 현재 기준 브랜치/커밋: `main` / `403f98d` (2026-10-11 16:06 KST)

## 1. 조사 목적과 결론

세 저장소에 흩어진 기능을 하나의 제품 정의로 통합한다. 이 문서는 기능을 많이 나열하기 위한 목록이 아니다. 사용자가 실제로 브랜드를 만들고, 수정하고, 의사결정을 보존하고, 결과물을 외부에 전달하는 데 필요한 최소 기능을 구분한다.

**제품 정의:** NAME TAG는 초기 사업 아이디어를 브랜드 전략·고객·시장·시각 정체성으로 정리하고, AI와 함께 계속 개선하며, 최종 브랜드 가이드로 내보내는 **AI Brand Workspace**다.

**가장 중요한 제품 원칙**
- 채팅은 입력 방식이고, 브랜드 작업공간이 제품의 중심이다.
- 브랜드의 확정 정보는 하나의 정규 데이터(BrandState)에 저장한다.
- AI 결과는 초안(Artifact) 또는 변경 제안(Proposal)으로 만든다.
- 사용자의 승인 전에는 AI가 확정 브랜드 정보를 직접 덮어쓰지 않는다.
- 모든 변경은 버전, 스냅샷, 이력으로 추적할 수 있어야 한다.
- 첫 출시에서는 전 기능을 갖춘 자율 에이전트보다, 핵심 흐름이 끊김 없이 작동하는 것이 우선이다.

## 2. 저장소별 조사 결과

### 2.1 `Name_Tag_Streamlit` — 기능 검증용 프로토타입

저장소: https://github.com/Joseph-Ai-py/Name_Tag_Streamlit  
최근 확인 커밋: `64fe74f` (2026-10-11)

**확인된 주요 기능**
- Section O: 업종·브랜드 감성·타겟·키워드 입력, 인터뷰 질문, 브랜드 후보 생성, 후보 필드별 조합
- Section A: 철학, 에센스, 미션·비전, 스토리, 포지셔닝, 브랜드 약속 생성
- Section B: 타겟, 페르소나, 고객 여정, 고객 SWOT, 비즈니스 모델
- Section C: 색상, 타이포그래피, 비주얼 무드, 디자인 원칙
- Section DE: 로고 및 캐릭터 가이드와 이미지 생성
- 필드 단위 재생성, 사이드바 직접 수정, 인터뷰 답변/선택 상태 보존
- Brand DNA 구성, Decision Trace 기록, 브랜드 간 오염 문구 검사
- HTML 미리보기 및 WeasyPrint 기반 PDF 생성, PDF 직전 무결성 검사

**구조상 한계**
- `state.py`의 핵심 데이터는 Streamlit `session_state`에 저장된다. 브라우저 세션 중심의 프로토타입이며 다중 사용자·영구 브랜드 저장소의 기반은 아니다.
- O/A/B/C/DE의 단계별 생성 로직이 분리되어 있어 기능 검증에는 유용하지만, 지속적 대화형 Workspace라는 제품 모델과는 다르다.
- 이 저장소는 기능 레퍼런스로 보존하되, 주 제품의 실행 기반으로 확장하지 않는 편이 낫다.

**가져갈 가치**
- 인터뷰 질문의 목적과 출력 구조
- 4개 후보의 필드별 믹스앤매치
- A/B/C/DE의 실질적인 브랜드 콘텐츠 필드
- Brand DNA 정규화, Decision Trace, 교차 브랜드 오염 방지
- HTML/PDF 가이드 조립 로직과 시각적 결과물

참고 파일: [README](https://github.com/Joseph-Ai-py/Name_Tag_Streamlit/blob/main/README.md), [app.py](https://github.com/Joseph-Ai-py/Name_Tag_Streamlit/blob/main/app.py), [models.py](https://github.com/Joseph-Ai-py/Name_Tag_Streamlit/blob/main/models.py), [state.py](https://github.com/Joseph-Ai-py/Name_Tag_Streamlit/blob/main/state.py), [brand_dna.py](https://github.com/Joseph-Ai-py/Name_Tag_Streamlit/blob/main/brand_dna.py), [pdf_service.py](https://github.com/Joseph-Ai-py/Name_Tag_Streamlit/blob/main/pdf_service.py).

### 2.2 `Name_Tag` — 초기 웹 제품과 여러 세대 코드의 혼재

저장소: https://github.com/Joseph-Ai-py/Name_Tag  
최근 확인 커밋: `cece014` (2026-10-11)

**확인된 주요 기능**
- React + Vite 프론트엔드와 FastAPI 백엔드
- Section O의 인터뷰/브랜드 후보 생성/필드별 재생성
- A/B/C/DE 단계별 콘텐츠 생성
- 로고·캐릭터 생성, HTML/PDF 가이드 출력
- 프론트엔드 인터뷰 건너뛰기, 뒤로/앞으로 이동, 선택값 보존, 미리보기 관련 개선 기록

**확인된 유지보수 위험**
- 저장소 루트의 초기 웹 제품, `streamlit/`, `notebook_backend/`, `V2/Name_Tag/`라는 중첩 V2 사본이 공존한다. 동일한 도메인 로직과 산출물이 여러 위치에 생길 수 있어 어느 구현이 기준인지 혼란을 만든다.
- 루트 `plan.md`는 기존 마법사 UI 개선과 남은 작업을 기록한 문서다. 현재 V2 제품 범위 정의서로 사용하면 안 된다.
- 루트 README의 후보 수 설명에 3개와 4개가 혼재한다. 실제 Section O/후보 선택 흐름과 문서의 표현을 한 번 더 정합화해야 한다.
- `backend/routers/section_o.py`의 `ORegenRequest`는 `brand_data` 필드를 정의하지만 재생성 함수는 `req.brand_info`를 참조한다. 이 경로는 요청 모델과 구현이 맞지 않아 오류가 날 가능성이 높다.
- PDF 빌더가 별도 `notebook_backend` 파일을 동적 로딩하는 경로 의존성을 갖고 있어 배포 위치에 따라 취약할 수 있다.

**판단**
- 이 저장소는 기존 사용자 경험, 프롬프트, 콘텐츠 구조 및 PDF 레이아웃의 레퍼런스로 사용한다.
- 새로운 제품 기능은 이 저장소에 추가하지 않는다. 중첩된 V2 사본을 포함해 장기적으로 단일 기준 저장소로 정리해야 한다.

참고 파일: [README](https://github.com/Joseph-Ai-py/Name_Tag/blob/main/README.md), [Section O API](https://github.com/Joseph-Ai-py/Name_Tag/blob/main/backend/routers/section_o.py), [Section O UI](https://github.com/Joseph-Ai-py/Name_Tag/blob/main/frontend/src/pages/SectionO.tsx), [legacy plan.md](https://github.com/Joseph-Ai-py/Name_Tag/blob/main/plan.md).

### 2.3 `Name_Tag_V2` — 주 제품으로 삼을 가장 적절한 기반

저장소: https://github.com/Joseph-Ai-py/Name_Tag_V2  
현재 기준 커밋: `403f98d` (2026-10-11 16:06 KST)

**이미 구현된 핵심 기반**
- 회원가입/로그인, HttpOnly 세션, 현재 사용자 조회, 브랜드 멤버십/권한 확인
- 사용자별 Brand 및 BrandState 격리
- BrandState 단일 저장소와 부분 수정, 변경 경로 검증, 버전 충돌 방지
- Conversation/Message 저장 및 Agent Chat
- Skill/Tool Registry, LLM Gateway, Agent Run/Tool Call 기록
- Artifact 초안 저장
- Proposal 생성 → 승인 → 적용 흐름
- 적용 시 Snapshot 및 History 생성, 오래된 Snapshot 복원
- Quick/Deep Research Job, Report, Source, Finding 및 Finding → Proposal 연결
- Asset 메타데이터 CRUD
- Document/Block CRUD
- JSON Export

**실제 코드에서 확인한 중요한 설계**
1. `backend/app/services/brand_state_service.py`는 브랜드별 단일 BrandState를 만들고, 부분 변경을 병합하며, 변경 전 Snapshot과 History를 남긴다.
2. `backend/app/services/proposal_service.py`는 승인된 Proposal만 적용하며, Proposal 생성 당시 버전과 현재 버전이 다르면 충돌로 처리한다.
3. `backend/app/agent/core.py`는 대화 기록과 브랜드 맥락을 구성하고, Tool/Skill을 사용해 응답·Artifact·Proposal·Research Job을 만든다.
4. `backend/app/api/brand_state.py`, `proposals.py`, `agent.py`는 각 요청에서 브랜드 멤버십 및 수정 권한을 검사한다.
5. `backend/tests/`에는 인증/브랜드 격리, BrandState, Proposal, Snapshot, Agent, Conversation, Research, Asset/Document, Export, Tool/Skill 테스트가 있다. 확인된 테스트 파일은 16개다. README에는 24 passed라고 적혀 있지만 이번 조사는 테스트 명령을 실제 실행하지 않았으므로 현재 통과 여부를 보증하지 않는다.

**현재 미완성 또는 과도한 영역**
- README는 실제 Web Search provider, Deep Research의 운영용 백그라운드 실행, PDF/Brand Kit Export, Object Storage 파일 업로드, 보안 보강, 프론트엔드 기능 연결을 진행 중으로 분류한다.
- `backend/app/api/export.py`는 `build_json_export`를 호출한다. 현재 Export는 JSON이고 PDF Brand Kit Export가 아니다.
- `backend/app/api/assets.py`와 Asset 모델은 `storage_path`와 메타데이터를 저장한다. 이 API 자체가 파일 업로드/오브젝트 스토리지를 구현한 것은 아니다.
- Legacy migration 문서는 Gemini 이미지 생성과 파일 저장 adapter, PDF 출력이 아직 V2로 완전히 이식되지 않았다고 명시한다.
- `frontend/src/app/App.tsx`에 큰 UI 구현이 집중되어 있다. 반면 현재 트리의 `frontend/src/` 파일 170개 중 162개가 0바이트다. 기능별 파일 구조가 실질적으로 분리·구현됐다고 볼 수 없다.
- `docs/`의 파일 9개 중 6개가 0바이트다. `docs/architecture/overview.md`의 P0~P3 체크리스트도 현재 코드/테스트와 일치하도록 갱신이 필요하다.
- 저장소에 `__pycache__`/컴파일된 `.pyc` 파일 195개와 SQLite 데이터베이스 2개가 추적되고 있다. 제품 기능은 아니지만 배포·보안·저장소 품질을 위해 별도 정리해야 한다.
- `run_employee_meeting`과 회의 API/모델/테스트는 현재 핵심 브랜드 생성 흐름에 반드시 필요한 기능이 아니다. 초기 제품 범위에서는 제외하는 편이 낫다.

참고 파일: [README](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/README.md), [Architecture overview](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/docs/architecture/overview.md), [Legacy migration inventory](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/docs/legacy-skill-migration.md), [BrandState service](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/backend/app/services/brand_state_service.py), [Proposal service](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/backend/app/services/proposal_service.py), [Agent core](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/backend/app/agent/core.py), [Export API](https://github.com/Joseph-Ai-py/Name_Tag_V2/blob/main/backend/app/api/export.py).

## 3. 핵심 기능 정의

기능을 “기술적으로 구현할 수 있는가”가 아니라 “사용자가 처음부터 끝까지 브랜드를 완성하고 관리할 수 있는가”로 평가한다.

| 기능 | 사용자에게 주는 가치 | 우선순위 | 판단 |
| --- | --- | --- | --- |
| 계정/브랜드별 데이터 격리 | 여러 사용자의 브랜드 정보 보호 | P0 | 필수 |
| 브랜드 초기 입력 및 인터뷰 | 막연한 아이디어를 구조화 | P0 | 필수 |
| 브랜드 후보 생성·선택 | 이름/의미/슬로건/스토리/컬러 방향 결정 | P0 | 필수 |
| BrandState 작업공간 | 확정 정보를 한 곳에서 관리 | P0 | 필수 |
| AI 컨설턴트 대화 | 저장된 브랜드 맥락을 바탕으로 개선 | P0 | 필수 |
| Artifact/Proposal/승인 | AI 초안과 확정 결정을 분리 | P0 | 필수 |
| 버전/스냅샷/이력 복원 | 잘못된 변경의 복구 | P0 | 필수 |
| 로고 생성 및 자산 보관 | 실사용 가능한 시각 결과물 | P0 | 필수 |
| 브랜드 가이드 PDF | 제품의 최종 전달물 | P0 | 필수 |
| 출처가 있는 Quick Research | 시장·고객 판단의 근거 | P1 | 핵심 다음 단계 |
| 캐릭터 생성 | 시각 아이덴티티 확장 | P1 | 선택 기능 |
| Deep Research 운영 worker | 오래 걸리는 심층 조사 자동화 | P1 | 이후 단계 |
| 협업자 초대/고급 역할 | 팀 단위 공동작업 | P1 | 수요 확인 후 |
| Block Editor | 문서 내부 편집 | P2 | PDF/브랜드 정보 편집 후 필요성 재평가 |
| AI Employee 회의/다중 에이전트 | 여러 에이전트의 토론 | P2 | 필수 아님 |
| RAG, Redis, SSE, MCP, 멀티모델 | 플랫폼 확장성 | P2 | 실제 병목이 생긴 뒤 |

## 4. 권장 제품 흐름

1. 사용자가 회원가입하고 브랜드 Workspace를 만든다.
2. 업종/서비스, 고객, 키워드, 감성을 입력하고 AI 인터뷰를 진행한다. 인터뷰를 건너뛰고 빠르게 시작할 수도 있다.
3. 브랜드 후보를 생성하고 이름·의미·슬로건·스토리·대표 컬러를 필드별로 조합해 확정한다.
4. BrandState에 사업·고객·시장·브랜드 전략·비주얼 정보를 저장한다.
5. 사용자는 Workspace에서 정보를 직접 수정하거나 AI 컨설턴트에게 특정 영역의 개선을 요청한다.
6. AI는 근거와 함께 Artifact/Proposal을 만든다. 확정 정보 변경은 사용자가 검토하고 승인한 뒤에만 적용한다.
7. 사용자는 로고를 생성하고 시각 자산으로 보관한다.
8. 전체 정보를 Brand DNA 기준으로 검사한 뒤 PDF 브랜드 가이드를 출력한다.
9. 모든 주요 변경은 이력으로 확인하고 필요한 경우 Snapshot을 복원한다.

## 5. 아키텍처 원칙 및 금지선

- **기준 저장소는 V2 하나:** 기존 두 저장소는 기능/디자인/프롬프트 레퍼런스다.
- **BrandState가 단일 원천:** 동일한 브랜드 사실을 Artifact, 별도 프론트 상태, 별도 DB에 중복 확정하지 않는다.
- **AI는 직접 확정 데이터를 덮어쓰지 않는다:** AI 산출물과 확정 상태 사이에 사용자 승인 단계를 둔다.
- **Legacy schema를 무비판적으로 복제하지 않는다:** 상세 생성 결과는 Artifact로 보존하고, 브랜드 운영에 필요한 요약 필드만 BrandState에 반영한다.
- **단계별 마법사에 종속되지 않는다:** O/A/B/C/DE는 도메인 역량/프롬프트의 출처로 사용하고, 새로운 제품 UI는 Workspace와 작업 단위로 설계한다.
- **실제 파일 저장과 메타데이터 저장을 구분한다:** Asset row만 만든 것을 파일 업로드 완료라고 표현하지 않는다.
- **실제 PDF가 없으면 PDF Export 완료라고 표현하지 않는다:** 현재 JSON Export와 PDF Brand Kit은 다른 기능이다.
- **필요하기 전에 인프라를 추가하지 않는다:** RAG/Redis/SSE/MCP/worker cluster/multi-model은 MVP 목표가 아니다.

## 6. 조사 한계와 검증 필요 항목

- 이번 조사는 2026-11-14 기준 GitHub `main` 브랜치의 README, 파일 트리, 주요 서비스/API/모델/테스트 소스를 읽은 정적 코드 조사다.
- 테스트, Docker 실행, 외부 Gemini API, 실제 이미지 생성, 파일 업로드, 실제 PDF 렌더링을 실행하지 않았다.
- 따라서 기존 테스트가 현재 모두 통과하는지, 실제 배포 환경에서 전체 흐름이 동작하는지는 미확인이다.
- V2의 실제 앱 동작은 프론트엔드 `App.tsx`와 백엔드 API를 함께 실행해 별도 E2E 확인이 필요하다.
- 이 문서는 범위와 의사결정을 위한 연구 결과이며, 구현 완료 보고서가 아니다.
