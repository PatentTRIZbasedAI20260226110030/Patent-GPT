# Patent-GPT

**새로운 아이디어를 얻기 위한 트리즈(TRIZ) 활용 인공지능 엔진 서비스**

> 5조 · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026 · 발표일: 2026-03-04

[English README](README.md)

---

## 차례

1. [기획의도](#1-기획의도)
2. [AS-IS: 시장/경쟁사 분석](#2-as-is-시장경쟁사-분석)
3. [사용자 분석](#3-사용자-분석)
4. [TO-BE: 제안하는 AI 기능 컨셉](#4-to-be-제안하는-ai-기능-컨셉)
5. [서비스 상세: 아키텍처 및 Flow Chart](#5-서비스-상세-아키텍처-및-flow-chart)
6. [기대 효과](#6-기대-효과)
7. [빠른 시작](#빠른-시작)
8. [프로젝트 구조](#프로젝트-구조)
9. [API](#api)
10. [로드맵](#로드맵)

---

## 1. 기획의도

**TRIZ**(Theory of Solving Inventive Problem)는 구 소련 겐리히 알츠슐러(Genrich Altshuller)에 의해 제창된 **발명문제 해결을 위한 체계적 방법론**입니다.

일상생활을 하며 한두 가지 불편한 점을 느낀 경험은 누구나 있습니다. 하지만 막상 이런 불편한 점들을 해결하려고 하면 적당한 방법을 찾지 못하는 경우가 일반적입니다.

본 서비스는 **TRIZ 40가지 발명원리**를 활용한 인공지능 엔진을 통해, 막연한 문제 인식을 **구체적인 특허 아이디어**와 **실행 가능한 인사이트**로 전환하는 것을 목표로 합니다.

**핵심 가치:**

```
키워드 입력 → 특허 아이디어 생성 → 특허로서의 가치 평가
```

---

## 2. AS-IS: 시장/경쟁사 분석

현재 특허 분야 AI 서비스들은 주로 아이디어에서 머무르지 않고 **명세서 작성**까지를 서비스합니다.

| 서비스 | 설명 |
| :-- | :-- |
| **젠아이피 (GenIP)** | 변리사의 특허 명세서 작성 업무를 돕기 위한 생성형 AI 기반 명세서 서비스 'Gen-D'를 변리사들에게 제공 |
| **패튼에프티 (PatentFT)** | 키워드를 입력하면 이를 분석해 특허 명세서 초안을 작성해 주는 'PatenDraft' 프로그램 |
| **특허청 (KIPO)** | AI 학습에 활용 가능한 지식재산 데이터 7종을 특허정보활용서비스(KIPRISplus)를 통해 무료 개방 |

> **기존 서비스의 한계:** 이미 아이디어가 있는 상태에서 명세서 작성을 돕는 데 집중합니다.
> Patent-GPT는 그보다 앞선 단계 — **아이디어 자체를 발굴하고 가치를 평가**하는 것부터 시작합니다.

---

## 3. 사용자 분석

### 타겟 페르소나: 개인 발명가 / 예비 창업자

| 항목 | 내용 |
| :-- | :-- |
| **이름** | 정민아 (31세) |
| **직업** | 예비 창업자 |
| **상황** | 막연히 특허 하나는 있어야 하지 않을까라는 생각을 하고 있으나 구체적 기술은 없음 |
| **목표** | 사업화 가능한 특허 아이디어 발굴, 정부지원사업 지원 |

### Pain Point

- 무엇을 만들어야 할지 모름
- 특허 검색은 하지만 인사이트 도출이 어려움
- 기술 트렌드 이해가 부족함

### Needs (핵심 사용자 플로우)

```
키워드 입력 → 특허 아이디어 생성 → 특허로서 가치가 있는지 평가
```

### User Journey Map

| 단계 | 인지 | 탐색 | 사용 | 평가 |
| :-- | :-- | :-- | :-- | :-- |
| **행동** | 불편함을 인식 | 키워드로 검색 시작 | TRIZ 기반 아이디어 생성 | 특허 가치/신규성 확인 |
| **감정** | 막연함 | 기대감 | 구체화되는 느낌 | 실행 가능성 판단 |
| **터치포인트** | 일상 경험 | Patent-GPT 접속 | 결과 확인 | 평가 리포트 |

---

## 4. TO-BE: 제안하는 AI 기능 컨셉

### 기존 서비스와의 핵심 차별성

| 구분 | 기존 서비스 (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| **초점** | 명세서 작성 보조 | **아이디어 발굴 + 가치 평가** |
| **방법론** | 일반 LLM 지식 | TRIZ 40 원리 Few-Shot 프롬프팅 |
| **검색 방식** | 단순 키워드 매칭 | 의미 + 키워드 + 리랭킹 (하이브리드) |
| **작동 방식** | 1회성 문답 (Stateless) | 조건부 재설계 루프 (Agentic) |
| **결과물** | 비정형 텍스트 | Pydantic 검증 JSON → DOCX |

### 적용 기술

| 구분 | 기술 |
| :-- | :-- |
| 언어 | Python 3.11+, TypeScript 5 |
| 백엔드 | FastAPI, Uvicorn |
| 프론트엔드 | Next.js 16, React 18, Tailwind CSS, Shadcn UI |
| LLM 오케스트레이션 | LangChain, LangGraph |
| LLM | OpenAI GPT-4o-mini (`langchain-openai`) |
| 임베딩 | OpenAI text-embedding-3-small |
| 벡터 DB | ChromaDB (로컬, in-process) |
| 검색 | BM25 (rank-bm25) + Cross-Encoder (sentence-transformers) |
| 특허 데이터 | KIPRISplus Open API |
| 출력 | Pydantic Structured Output + python-docx |
| 디자인 | Figma ([9화면 와이어프레임](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)) |
| 테스트 | pytest, pytest-asyncio |
| 린팅 | Ruff (백엔드), ESLint + Prettier (프론트엔드) |

---

## 5. 서비스 상세: 아키텍처 및 Flow Chart

**Service Layer + LangGraph Core**
FastAPI 라우트 → 서비스 레이어 → LangGraph(회피 설계 루프에만 적용).
각 파이프라인 단계는 독립적으로 테스트 가능한 서비스로 분리되어 있습니다.

```text
┌───────────────────────────────────────────────────┐
│                  FastAPI Server                    │
├───────────────────────────────────────────────────┤
│  POST /api/v1/patent/generate                     │
│                    │                              │
│                    ▼                              │
│  ┌────────────────────────────────────────────┐   │
│  │         PatentService (Orchestrator)        │   │
│  │                                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │ Stage 1  │→ │ Stage 2  │→ │ Stage 3  │ │   │
│  │  │   TRIZ   │  │  선행특허 │  │  추론    │ │   │
│  │  │  분류기  │  │  검색기  │  │ 에이전트 │ │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘ │   │
│  │                                   │        │   │
│  │                   ┌───────────────┘        │   │
│  │                   ▼                        │   │
│  │  유사도>80%? ─YES─→ 회피 설계 루프          │   │
│  │       │             (최대 3회 시도)         │   │
│  │       NO                    │              │   │
│  │       │         ◄───────────┘              │   │
│  │       ▼                                    │   │
│  │  ┌──────────┐                              │   │
│  │  │ Stage 4  │ → JSON + DOCX               │   │
│  │  │  초안    │                              │   │
│  │  │ 생성기   │                              │   │
│  │  └──────────┘                              │   │
│  └────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  ┌──────────┐        ┌───────────┐
  │ ChromaDB │        │ KIPRISplus│
  │(벡터 DB) │        │  Open API │
  └──────────┘        └───────────┘
```

### 4단계 파이프라인

| 단계 | 서비스 | 설명 | 기술 |
| :--: | :-- | :-- | :-- |
| 1 | **TRIZ 분류기** | 모순 행렬 + LLM (또는 ML 모델)으로 문제를 TRIZ 원리에 매핑 | GPT-4o-mini / XGBoost |
| 2 | **선행특허 검색기** | KIPRISplus 데이터 하이브리드 검색 + 정밀 리랭킹 | BM25 + ChromaDB + Cross-Encoder |
| 3 | **추론 에이전트** | 유사도 임계값 초과 시 자율 재설계 (회피 설계) | LangGraph 회피 루프 |
| 4 | **초안 생성기** | KIPO 형식 JSON + DOCX 특허 초안 생성 | Pydantic `with_structured_output` + python-docx |

---

## 6. 기대 효과

| 관점 | 기대 효과 |
| :-- | :-- |
| **개인 발명가** | TRIZ 전문 지식 없이도 체계적 발명 방법론을 활용한 아이디어 도출 가능 |
| **예비 창업자** | 사업화 가능한 특허 아이디어를 빠르게 발굴하고 가치를 사전 검증 |
| **R&D 엔지니어** | 기존 특허 대비 차별화된 설계 대안을 자동으로 탐색 |
| **특허 산업** | 아이디어 진입 장벽을 낮춰 개인/중소 발명자의 특허 생태계 참여 확대 |

---

## 빠른 시작

### 사전 준비

- Python 3.11+
- OpenAI API 키 (필수 — LLM 추론 + 임베딩)
- KIPRISplus API 키 (선택, [공공데이터포털](https://www.data.go.kr/)에서 발급)

### 설치

```bash
git clone https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT.git
cd Patent-GPT

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

cp .env.example .env
# .env를 열어 API 키를 입력하세요
```

### 환경 변수

```env
# 필수
OPENAI_API_KEY=sk-...                  # OpenAI API 키 (LLM 추론 + 임베딩)

# 선택
GOOGLE_API_KEY=...                     # Google Gemini 키 (하위 호환용)
KIPRIS_API_KEY=...                     # KIPRISplus API 키 (외부 특허 검색)

# 모델 설정
LLM_MODEL=gpt-4o-mini                 # 전체 파이프라인 LLM 모델
EMBEDDING_MODEL=text-embedding-3-small

# 검색 설정
SIMILARITY_THRESHOLD=0.5               # 이 값 초과 시 회피 루프 실행
MAX_EVASION_ATTEMPTS=3                 # 최대 재설계 시도 횟수
RETRIEVAL_TOP_K=20                     # 하이브리드 검색 후보 수
RERANK_TOP_K=5                         # 리랭킹 후 최종 결과 수
CHROMA_PERSIST_DIR=./data/chromadb
ALLOWED_ORIGINS=["http://localhost:3000"]  # CORS 허용 출처

# 지능 기능
TRIZ_ROUTER=llm                        # "llm" (모순 행렬) 또는 "ml" (XGBoost)
ML_MODEL_PATH=./data/models/triz_classifier.joblib
FAITHFULNESS_THRESHOLD=0.8             # RAGAS 평가 통과 임계값
ENABLE_AUTO_EVALUATION=false           # 생성 후 RAGAS 자동 실행
```

### 특허 데이터 적재

```bash
python scripts/ingest_patents.py
```

### 백엔드 실행

```bash
uvicorn app.main:app --reload
```

### 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
# http://localhost:3000 에서 확인
```

### 테스트

```bash
pytest
```

---

## 프로젝트 구조

```text
Patent-GPT/
├── app/                            # 백엔드 (FastAPI)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── admin.py            # 관리자 엔드포인트 (데이터 적재 트리거)
│   │   │   ├── health.py           # 헬스체크 엔드포인트
│   │   │   └── patent.py           # 특허 생성 엔드포인트
│   │   └── schemas/
│   │       ├── request.py          # PatentGenerateRequest, PatentSearchRequest DTO
│   │       └── response.py         # PatentGenerateResponse, SimilarPatent DTO
│   ├── models/
│   │   ├── evaluation.py           # RAGAS EvaluationResult 모델
│   │   ├── patent_draft.py         # PatentDraft 도메인 모델 (KIPO 형식)
│   │   ├── session.py              # 대화 메모리 (SessionStore, SessionHistory)
│   │   ├── state.py                # LangGraph AgentState
│   │   └── triz.py                 # TRIZ 원리 + ContradictionMatrix 모델
│   ├── prompts/                    # LLM 프롬프트 모음
│   ├── services/
│   │   ├── draft_generator.py      # Stage 4: Pydantic 구조화 출력 + DOCX
│   │   ├── evaluation_service.py   # RAGAS 평가 (충실도, 관련성, 재현율)
│   │   ├── memory_service.py       # 대화 메모리 서비스
│   │   ├── ml_classifier.py        # ML 기반 TRIZ 분류기 (XGBoost + TF-IDF)
│   │   ├── patent_searcher.py      # Stage 2: BM25 + ChromaDB + Cross-Encoder
│   │   ├── patent_service.py       # 오케스트레이터: 전체 파이프라인 연결
│   │   ├── reasoning_agent.py      # Stage 3: LangGraph 회피 루프
│   │   └── triz_classifier.py      # Stage 1: LLM/ML 이중 라우터 TRIZ 분류
│   ├── utils/
│   │   ├── docx_exporter.py        # PatentDraft → DOCX 변환
│   │   └── kipris_client.py        # KIPRISplus 비동기 API 클라이언트
│   ├── config.py                   # pydantic-settings 기반 환경 설정
│   └── main.py                     # FastAPI 앱 엔트리포인트
├── frontend/                       # 프론트엔드 (Next.js 16 + React 18)
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx            # S-01 랜딩
│   │   │   ├── generate/page.tsx   # S-02~04 생성 (입력/로딩/결과)
│   │   │   └── search/page.tsx     # S-05 선행특허 검색
│   │   ├── components/
│   │   │   ├── ui/                 # Shadcn UI 기본 컴포넌트
│   │   │   ├── PatentForm.tsx      # 문제 입력 폼
│   │   │   ├── LoadingSteps.tsx    # 4단계 파이프라인 진행 표시
│   │   │   ├── ResultPanel.tsx     # 생성 결과 표시
│   │   │   ├── TrizCard.tsx        # TRIZ 원리 카드
│   │   │   ├── PatentCard.tsx      # 유사 특허 카드
│   │   │   └── DownloadButton.tsx  # DOCX 다운로드
│   │   ├── lib/
│   │   │   ├── api.ts              # 백엔드 API 클라이언트
│   │   │   └── utils.ts            # 공유 유틸리티
│   │   └── types/
│   │       └── patent.ts           # TypeScript 타입 (백엔드 스키마 동기화)
│   └── docs/
│       ├── SCREEN_DEFINITION.md    # 화면별 상세 정의서
│       ├── FIGMA_GUIDE.md          # Figma 디자인 시스템 가이드
│       └── HANDOFF.md              # 작업 맥락 전달 문서
├── data/
│   ├── triz_principles.json        # TRIZ 40가지 발명 원리
│   └── triz_contradiction_matrix.json  # 39×39 알츠슐러 모순 행렬
├── scripts/
│   ├── ingest_patents.py           # KIPRISplus → ChromaDB 배치 적재
│   ├── ingest_sample.py            # LLM 생성 샘플 데이터 → ChromaDB
│   └── train_triz_classifier.py    # TF-IDF + XGBoost TRIZ 학습 파이프라인
├── tests/                          # 모듈별 단위 테스트
├── .env.example
├── pyproject.toml
├── CLAUDE.md
└── LICENSE
```

---

## API

> **API 계약의 기준(Source of Truth):** [`tests/test_patent_route.py`](tests/test_patent_route.py) 기반 테스트 우선 계약.  
> 본 섹션은 문서 단독 가정이 아니라 테스트로 검증된 동작을 기준으로 작성합니다.

### `GET /api/v1/health`

헬스체크 엔드포인트입니다.

```json
{ "status": "healthy", "version": "0.1.0" }
```

### `POST /api/v1/patent/generate`

전체 4단계 파이프라인 실행: TRIZ 분류 → 선행 특허 검색 → 회피 루프(필요 시) → 초안 생성.

**최소 요청 바디 (route 테스트 기준):**

```json
{
  "problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"
}
```

**요청 예시:**

```json
{
  "problem_description": "기기를 얇게 유지하면서 발열을 줄여야 한다",
  "technical_field": "전자기기",
  "max_evasion_attempts": 3
}
```

`max_evasion_attempts` 범위: `1~5`

**검증 실패 케이스 (route 테스트 기준):**

```json
{
  "problem_description": ""
}
```

예상 결과: `422 Unprocessable Entity`

**응답 예시:**

```json
{
  "patent_draft": {
    "title": "...",
    "abstract": "...",
    "background": "...",
    "problem_statement": "...",
    "solution": "...",
    "claims": ["...", "...", "..."],
    "effects": "..."
  },
  "triz_principles": [...],
  "similar_patents": [...],
  "reasoning_trace": ["[아이디어 생성] ...", "[선행기술 조사] ...", "[완료] ..."],
  "draft_id": "patent_draft_ab12cd34",
  "novelty_score": 0.67,
  "threshold": 0.5,
  "docx_download_url": "data/drafts/patent_draft_ab12cd34.docx"
}
```

`triz_principles[]`의 각 항목에는 UI 표시용 `matching_score`가 선택적으로 포함될 수 있습니다.

### `POST /api/v1/patent/generate/stream`

파이프라인 상태를 단계별로 전송하는 SSE 엔드포인트입니다.

### `GET /api/v1/patent/{draft_id}/docx`

생성된 특허 초안을 DOCX 파일로 다운로드합니다.
`docx_download_url`이 `data/drafts/patent_draft_ab12cd34.docx`라면
`draft_id=patent_draft_ab12cd34`로 호출하면 됩니다.

파일이 없으면(route 테스트 기준) `404 Not Found`를 반환합니다.

### `POST /api/v1/patent/search`

전체 파이프라인 없이 선행 특허 검색만 단독으로 수행합니다.

**최소 요청 바디 (route 테스트 기준):**

```json
{
  "query": "방열 구조"
}
```

선택 요청 필드: `top_k` (`1~50`, 기본값 `5`)

### `POST /api/v1/admin/ingest`

KIPRISplus에서 ChromaDB로 특허 데이터 적재를 트리거합니다.

---

## 로드맵

| 마일스톤 | 범위 | 상태 |
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | 프로젝트 스캐폴딩, 설정, 핵심 데이터 모델, FastAPI 스켈레톤, API 스키마 | ✅ 완료 |
| **v0.2.0 · Core Services** | TRIZ 분류기, KIPRISplus 클라이언트, 적재 스크립트, 하이브리드 특허 검색기, 프롬프트 라이브러리 | ✅ 완료 |
| **v0.3.0 · Agent & Output** | LangGraph 추론 에이전트, 초안 생성기(Pydantic + DOCX), PatentService 오케스트레이터 | ✅ 완료 |
| **v0.4.0 · Ship** | 라우트 연결, Ruff 린팅, 전체 테스트 스위트, 스모크 테스트 | ✅ 완료 |
| **v0.5.0 · UI/UX** | Figma 9화면 와이어프레임, Next.js 프론트엔드 스캐폴드, 컴포넌트 라이브러리, API 클라이언트 | ✅ 완료 |
| **v0.6.0 · Integration** | SSE 스트리밍 엔드포인트, CORS, 에러 처리, E2E 테스트, 문서 동기화 | ✅ 완료 |
| **v0.7.0 · Intelligence** | RAGAS 평가, TRIZ 모순 행렬, 대화 메모리, ML 분류기 | ✅ 완료 |
| **v0.8.0 · Simplification** | LLM 프로바이더 통일 (→ OpenAI GPT-4o-mini), 팩토리 중앙화, 싱글턴 서비스, 캐싱, 병렬 검색, 보안 강화 | ✅ 완료 |

### UI/UX 디자인

전체 사용자 플로우를 다루는 9화면 와이어프레임:

```
랜딩 → 문제 입력 → 분석 로딩 → TRIZ 결과 → 유사 특허 → 회피 설계 → 특허 초안 → 다운로드 | 빠른 검색
```

- **Figma:** [Patent-GPT 와이어프레임](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)
- **프로토타입:** [CodeSandbox](https://codesandbox.io/p/sandbox/mlc68g)

### MVP 범위 제한 사항

아래 기능은 후속 버전에서 구현 예정입니다:

- **Tool Calling** — TavilySearch / PythonREPL 도구 호출
- **HWP 출력** — 현재 DOCX만 지원
- **영속적 세션 저장소** — 현재 인메모리(LRU + TTL), DB 기반 예정

---

## 라이선스

[MIT](LICENSE)

---

## 팀

**5조** · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026
발표일: 2026-03-04
