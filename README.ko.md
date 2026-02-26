# TRIZ 활용 인공지능 엔진 서비스

TRIZ 활용 아이디어 발굴 AI 엔진 서비스

> 키워드나 일상의 문제를 입력하면, 본 서비스가 TRIZ 40가지 발명 원리를 활용해 창의적 아이디어를 생성하고, 기존 특허 대비 신규성을 평가한 뒤, 특허 가치를 확보하도록 자율 재설계하여 구조화된 특허 초안을 출력합니다.

[English README](README.md)

---

## 왜 이 서비스를 기획했는가?

일상에서 불편함을 느끼는 경험은 누구나 하지만, 그것을 구체적인 해결책 — 더 나아가 특허 가능한 발명 — 으로 연결하기는 쉽지 않습니다. 기존 AI 특허 서비스(젠아이피, 패튼에프티 등)는 이미 아이디어가 있는 상태에서 **명세서 작성**을 돕는 데 집중합니다. 본 서비스는 그보다 앞선 단계, 즉 TRIZ 방법론을 활용해 **아이디어 자체를 발굴**하는 것부터 시작하여 신규성 평가와 특허 초안 작성까지 이어줍니다.

---

## 타겟 사용자

| 페르소나 | 설명 |
| :-- | :-- |
| **개인 발명가** | 막연한 문제의식은 있지만, 이를 특허 가능한 아이디어로 체계화할 방법이 없는 사람 |
| **예비 창업자** | 사업화를 위해 특허가 필요하지만, 무엇을 만들어야 할지 모르는 사람 |
| **R&D 엔지니어** | 기술적 제약 안에서 빠르게 발명적 설계 대안을 탐색해야 하는 사람 |

**핵심 사용자 플로우:** 키워드 입력 → TRIZ 기반 아이디어 생성 → 특허 신규성 평가 → 구조화된 초안 출력

---

## 주요 기능

| 단계 | 기능 | 설명 | 기술 |
| :--: | :-- | :-- | :-- |
| 1 | **TRIZ 아이디어 생성기** | 키워드나 문제를 TRIZ 40가지 발명 원리로 분석하여 창의적 아이디어를 생성 | LLM Few-Shot Prompting |
| 2 | **특허 검색기** | 하이브리드 검색(BM25 + Vector) + Cross-Encoder 재정렬로 기존 특허 대비 신규성 평가 | Ensemble Retriever |
| 3 | **추론 에이전트** | 유사도가 80%를 초과하면 특허 가치를 확보하기 위해 회피 설계 루프를 자율 실행 | LangGraph |
| 4 | **초안 생성기** | JSON + DOCX 형태의 구조화된 특허 초안 생성 | Pydantic + python-docx |

---

## 아키텍처

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
│  │  │  Idea    │  │ Searcher │  │  Agent   │ │   │
│  │  │Generator │  │          │  │          │ │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘ │   │
│  │                                   │        │   │
│  │                   ┌───────────────┘        │   │
│  │                   ▼                        │   │
│  │  similarity>80%? ─YES─→ Evasion Loop       │   │
│  │       │                     │              │   │
│  │       NO                    │              │   │
│  │       │         ◄───────────┘              │   │
│  │       ▼                                    │   │
│  │  ┌──────────┐                              │   │
│  │  │ Stage 4  │ → JSON + DOCX               │   │
│  │  │  Draft   │                              │   │
│  │  │Generator │                              │   │
│  │  └──────────┘                              │   │
│  └────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  ┌──────────┐        ┌───────────┐
  │ ChromaDB │        │ KIPRISplus│
  │(Vector DB)│       │  Open API │
  └──────────┘        └───────────┘
```

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
OPENAI_API_KEY=sk-...            # OpenAI API key
KIPRIS_API_KEY=...               # KIPRISplus API key
LLM_MODEL=gpt-4o                # Generation model
LLM_MODEL_MINI=gpt-4o-mini      # Classification model
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.8         # Triggers evasion design if exceeded
MAX_EVASION_ATTEMPTS=3           # Max evasion loop iterations
RETRIEVAL_TOP_K=20               # Candidates from hybrid search
RERANK_TOP_K=5                   # Final results after reranking
CHROMA_PERSIST_DIR=./data/chromadb
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
│   │   │   ├── health.py         # 헬스체크 엔드포인트
│   │   │   └── patent.py         # 특허 생성 엔드포인트
│   │   └── schemas/
│   │       ├── request.py        # 요청 DTO
│   │       └── response.py       # 응답 DTO
│   ├── models/
│   │   ├── patent_draft.py       # 특허 초안 도메인 모델
│   │   ├── state.py              # LangGraph 에이전트 상태
│   │   └── triz.py               # TRIZ 원리 모델
│   ├── prompts/
│   │   └── classifier.py         # TRIZ 분류 프롬프트
│   ├── services/
│   │   └── triz_classifier.py    # TRIZ 분류 서비스
│   ├── utils/
│   │   └── kipris_client.py      # KIPRISplus 비동기 API 클라이언트
│   ├── config.py                 # pydantic-settings 기반 설정
│   └── main.py                   # FastAPI 앱 엔트리포인트
├── data/
│   └── triz_principles.json      # TRIZ 40가지 발명 원리
├── scripts/
│   └── ingest_patents.py         # ChromaDB 특허 적재 스크립트
├── tests/
├── .env.example
├── pyproject.toml
└── LICENSE
```

---

## 로드맵

개발은 [GitHub Issues](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT/issues)에서 관리되는 4개 마일스톤으로 진행됩니다.

| 마일스톤 | 범위 | 상태 |
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | 프로젝트 스캐폴딩, 설정, 핵심 데이터 모델, FastAPI 스켈레톤, API 스키마 (Tasks 1–6) | ✅ 완료 |
| **v0.2.0 · Core Services** | TRIZ 아이디어 생성기, KIPRISplus 클라이언트, 적재 스크립트, 하이브리드 특허 검색기, 프롬프트 라이브러리 (Tasks 7–11) | 🔧 진행 중 |
| **v0.3.0 · Agent & Output** | LangGraph 추론 에이전트, 초안 생성기(Pydantic + DOCX), PatentService 오케스트레이터 (Tasks 12–14) | 📋 예정 |
| **v0.4.0 · Ship** | 라우트 연결, 린팅, 전체 테스트 스위트, 서버 스모크 테스트 (Tasks 15–16) | 📋 예정 |

---

## API

### `GET /health`

헬스체크 엔드포인트입니다.

```json
{ "status": "ok" }
```

### `POST /api/v1/patent/generate`

키워드 또는 문제 설명으로부터 발명 아이디어와 특허 초안을 생성합니다.

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
    "solution": "..."
  }
}
```

---

## 라이선스

[MIT](LICENSE)

---

## 팀

**Team 5** · Track C (New AI Service) · AI Bootcamp 2026
