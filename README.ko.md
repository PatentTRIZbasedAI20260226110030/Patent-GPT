# Patent-GPT

**Agentic RAG 기반 발명 코파일럿 — TRIZ 방법론 + LLM을 결합한 특허 아이디어 생성 및 신규성 검증 플랫폼**

> 키워드나 일상의 문제를 입력하면, Patent-GPT가 TRIZ 40가지 발명 원리를 활용해 창의적 아이디어를 생성하고, 하이브리드 검색으로 선행 특허를 조사하며, 유사도가 높을 경우 자율 재설계하여 KIPO 형식의 구조화된 특허 초안(JSON + DOCX)을 출력합니다.

[English README](README.md)

---

## 왜 이 서비스를 기획했는가?

일상에서 불편함을 느끼는 경험은 누구나 하지만, 그것을 특허 가능한 발명으로 연결하기는 쉽지 않습니다. 기존 AI 특허 서비스(젠아이피, 패튼에프티 등)는 이미 아이디어가 있는 상태에서 **명세서 작성**을 돕는 데 집중합니다. Patent-GPT는 그보다 앞선 단계, 즉 TRIZ 방법론을 활용해 **아이디어 자체를 발굴**하는 것부터 시작하여 신규성 평가와 특허 초안 작성까지 이어줍니다.

**기존 서비스 대비 핵심 차별성:**

| 구분 | 기존 서비스 (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| **검색 방식** | 단순 키워드 매칭 | 의미 + 키워드 + 리랭킹 |
| **작동 방식** | 1회성 문답 (Stateless) | 조건부 재설계 루프 (Agentic) |
| **결과물** | 비정형 텍스트 | Pydantic 검증 JSON → DOCX |
| **방법론** | 일반 LLM 지식 | TRIZ 40 원리 Few-Shot 프롬프팅 |

---

## 타겟 사용자

| 페르소나 | 설명 |
| :-- | :-- |
| **개인 발명가** | 막연한 문제의식은 있지만, 이를 특허 가능한 아이디어로 체계화할 방법이 없는 사람 |
| **예비 창업자** | 사업화를 위해 특허가 필요하지만, 무엇을 만들어야 할지 모르는 사람 |
| **R&D 엔지니어** | 기술적 제약 안에서 빠르게 발명적 설계 대안을 탐색해야 하는 사람 |

**핵심 사용자 플로우:** 문제/키워드 입력 → TRIZ 기반 아이디어 생성 → 특허 신규성 평가 → 구조화된 초안 출력

---

## 아키텍처

**Approach B: Service Layer + LangGraph Core**
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
│  │  │   TRIZ   │  │  Patent  │  │ Reasoning│ │   │
│  │  │Classifier│  │ Searcher │  │  Agent   │ │   │
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
| 1 | **TRIZClassifier** | Few-Shot LLM 라우팅으로 문제를 TRIZ 원리에 매핑 | GPT-4o-mini, Few-Shot Prompting |
| 2 | **PatentSearcher** | KIPRISplus 데이터 하이브리드 검색 + 정밀 리랭킹 | BM25 + ChromaDB + Cross-Encoder |
| 3 | **ReasoningAgent** | 유사도 임계값 초과 시 자율 재설계 | LangGraph 회피 루프 |
| 4 | **DraftGenerator** | KIPO 형식 JSON + DOCX 특허 초안 생성 | Pydantic `with_structured_output` + python-docx |

---

## 기술 스택

| 구분 | 기술 |
| :-- | :-- |
| 언어 | Python 3.11+ |
| 프레임워크 | FastAPI, Uvicorn |
| LLM 오케스트레이션 | LangChain, LangGraph |
| LLM | OpenAI GPT-4o (생성), GPT-4o-mini (분류) |
| 임베딩 | OpenAI text-embedding-3-small |
| 벡터 DB | ChromaDB (로컬, in-process) |
| 검색 | BM25 (rank-bm25) + Cross-Encoder (sentence-transformers) |
| 특허 데이터 | KIPRISplus Open API |
| 출력 | Pydantic Structured Output + python-docx |
| 테스트 | pytest, pytest-asyncio |
| 린팅 | Ruff |

---

## 빠른 시작

### 사전 준비

- Python 3.11+
- OpenAI API 키
- KIPRISplus API 키 ([공공데이터포털](https://www.data.go.kr/)에서 발급)

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
OPENAI_API_KEY=sk-...                  # OpenAI API 키
KIPRIS_API_KEY=...                     # KIPRISplus API 키
LLM_MODEL=gpt-4o                       # 생성 모델
LLM_MODEL_MINI=gpt-4o-mini             # 분류 모델
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.8               # 이 값 초과 시 회피 루프 실행
MAX_EVASION_ATTEMPTS=3                 # 최대 재설계 시도 횟수
RETRIEVAL_TOP_K=20                     # 하이브리드 검색 후보 수
RERANK_TOP_K=5                         # 리랭킹 후 최종 결과 수
CHROMA_PERSIST_DIR=./data/chromadb
```

### 특허 데이터 적재

```bash
# 검색 실행 전 KIPRISplus 특허 데이터를 ChromaDB에 적재합니다
python scripts/ingest_patents.py
```

### 실행

```bash
uvicorn app.main:app --reload
```

### 테스트

```bash
pytest
```

---

## 프로젝트 구조

```text
Patent-GPT/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── admin.py          # 관리자 엔드포인트 (데이터 적재 트리거)
│   │   │   ├── health.py         # 헬스체크 엔드포인트
│   │   │   └── patent.py         # 특허 생성 엔드포인트
│   │   └── schemas/
│   │       ├── request.py        # PatentGenerateRequest, PatentSearchRequest DTO
│   │       └── response.py       # PatentGenerateResponse, SimilarPatent DTO
│   ├── models/
│   │   ├── patent_draft.py       # PatentDraft 도메인 모델 (KIPO 형식)
│   │   ├── state.py              # LangGraph AgentState
│   │   └── triz.py               # TRIZ 원리 모델
│   ├── prompts/
│   │   ├── classifier.py         # TRIZ 분류 Few-Shot 프롬프트
│   │   ├── evasion.py            # 회피 설계 프롬프트
│   │   └── triz_expert.py        # TRIZ 전문가 페르소나 프롬프트
│   ├── services/
│   │   ├── draft_generator.py    # Stage 4: Pydantic 구조화 출력 + DOCX
│   │   ├── patent_searcher.py    # Stage 2: BM25 + ChromaDB + Cross-Encoder
│   │   ├── patent_service.py     # 오케스트레이터: 4단계 파이프라인 연결
│   │   ├── reasoning_agent.py    # Stage 3: LangGraph 회피 루프
│   │   └── triz_classifier.py    # Stage 1: LLM 기반 TRIZ 라우팅
│   ├── utils/
│   │   ├── docx_exporter.py      # PatentDraft → DOCX 변환
│   │   └── kipris_client.py      # KIPRISplus 비동기 API 클라이언트
│   ├── config.py                 # pydantic-settings 기반 환경 설정
│   └── main.py                   # FastAPI 앱 엔트리포인트
├── data/
│   └── triz_principles.json      # TRIZ 40가지 발명 원리
├── scripts/
│   └── ingest_patents.py         # KIPRISplus → ChromaDB 배치 적재
├── tests/
│   ├── test_config.py
│   ├── test_draft_generator.py
│   ├── test_health.py
│   ├── test_kipris_client.py
│   ├── test_models.py
│   ├── test_models_triz.py
│   ├── test_patent_route.py
│   ├── test_patent_searcher.py
│   ├── test_patent_service.py
│   ├── test_reasoning_agent.py
│   └── test_triz_classifier.py
├── wiki/
│   ├── Architecture.md
│   ├── Home.md
│   └── TRIZ_Methodology.md
├── .env.example
├── pyproject.toml
├── CLAUDE.md
└── LICENSE
```

---

## API

### `GET /health`

헬스체크 엔드포인트입니다.

```json
{ "status": "ok" }
```

### `POST /api/v1/patent/generate`

전체 4단계 파이프라인 실행: TRIZ 분류 → 선행 특허 검색 → 회피 루프(필요 시) → 초안 생성.

**요청 예시:**

```json
{
  "keyword": "portable device heat dissipation",
  "problem_description": "Need to reduce heat generation while keeping the device thin",
  "domain": "Electronics",
  "language": "ko"
}
```

**응답 예시:**

```json
{
  "triz_principles": [...],
  "inventive_idea": "...",
  "similar_patents": [...],
  "novelty_score": 0.72,
  "evasion_applied": true,
  "patent_draft": {
    "title": "...",
    "abstract": "...",
    "claims": [...],
    "background": "...",
    "problem_statement": "...",
    "solution": "...",
    "effects": "..."
  }
}
```

### `GET /api/v1/patent/{id}/docx`

생성된 특허 초안을 DOCX 파일로 다운로드합니다.

### `POST /api/v1/patent/search`

전체 파이프라인 없이 선행 특허 검색만 단독으로 수행합니다.

### `POST /api/v1/admin/ingest`

KIPRISplus에서 ChromaDB로 특허 데이터 적재를 트리거합니다.

---

## 로드맵

| 마일스톤 | 범위 | 상태 |
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | 프로젝트 스캐폴딩, 설정, 핵심 데이터 모델, FastAPI 스켈레톤, API 스키마 (Tasks 1–6) | ✅ 완료 |
| **v0.2.0 · Core Services** | TRIZ 분류기, KIPRISplus 클라이언트, 적재 스크립트, 하이브리드 특허 검색기, 프롬프트 라이브러리 (Tasks 7–11) | ✅ 완료 |
| **v0.3.0 · Agent & Output** | LangGraph 추론 에이전트, 초안 생성기(Pydantic + DOCX), PatentService 오케스트레이터 (Tasks 12–14) | ✅ 완료 |
| **v0.4.0 · Ship** | 라우트 연결, Ruff 린팅, 전체 테스트 스위트, 스모크 테스트 (Tasks 15–16) | ✅ 완료 |
| **v0.5.0 · Intelligence** | RAGAS 평가(Faithfulness/Relevancy/Recall), TRIZ 모순 행렬, 대화 메모리 | 📋 예정 |

---

## MVP 범위 제한 사항

기획서에는 포함되었으나 아직 구현되지 않은 기능들입니다:

- **RAGAS 평가** — 충실도(Faithfulness), 문맥 재현율(Context Recall) 등의 신뢰성 평가 지표 (기획서의 "Core Tech 5")
- **에이전트 Tool Calling** — TavilySearch / PythonREPL 도구 호출 (현재 회피 루프는 프롬프트 기반이며 도구 호출 아님)
- **TRIZ 모순 행렬** — 개선/악화 파라미터 매핑을 통한 정밀 원리 선택 (현재: 40가지 원리 플랫 리스트)
- **대화 메모리** — 멀티턴 세션 상태 유지 ("맥락 기억"); 현재 파이프라인은 요청별 무상태(Stateless)
- **프론트엔드** — API 전용 MVP; UI 미구현
- **HWP 출력** — 현재 DOCX만 지원

---

## 라이선스

[MIT](LICENSE)

---

## 팀

**Team 5** · Track C (신규 AI 서비스 기획) · AI 부트캠프 2026
발표일: 2026-03-04
