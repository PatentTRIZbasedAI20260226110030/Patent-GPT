# Patent-GPT Backend MVP Design

**Date:** 2026-02-26
**Approach:** Service Layer + LangGraph Core (Approach B)
**Scope:** Backend-first MVP - FastAPI + LangGraph + ChromaDB

---

## Decisions

| Decision | Choice |
|---|---|
| Scope | Backend-first MVP |
| LLM | OpenAI GPT-4o / GPT-4o-mini |
| Patent Data | KIPRISplus Open API |
| Vector DB | ChromaDB |
| TRIZ Router | Hybrid (LLM-based now, ML model swappable later) |
| Embeddings | OpenAI text-embedding-3-small |
| Output | JSON + DOCX export |
| Deployment | Local development only |

---

## 1. Project Structure

```
Patent-GPT/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings (API keys, model config)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── patent.py          # POST /api/v1/patent/generate
│   │   │   └── health.py          # GET /api/v1/health
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── request.py         # Input schemas
│   │       └── response.py        # Output schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── patent_service.py      # Main orchestrator
│   │   ├── triz_classifier.py     # TRIZ principle routing (LLM-based, swappable to ML)
│   │   ├── patent_searcher.py     # Hybrid search (BM25 + ChromaDB + reranking)
│   │   ├── reasoning_agent.py     # LangGraph evasion loop
│   │   └── draft_generator.py     # Pydantic structured output + DOCX export
│   ├── models/
│   │   ├── __init__.py
│   │   ├── patent_draft.py        # PatentDraft Pydantic model
│   │   ├── triz.py                # TRIZ principle definitions & contradiction matrix
│   │   └── state.py               # LangGraph state schema
│   ├── prompts/
│   │   ├── triz_expert.py         # System prompt + few-shot examples
│   │   ├── classifier.py          # TRIZ routing prompt
│   │   └── evasion.py             # Evasion design prompt
│   └── utils/
│       ├── __init__.py
│       ├── kipris_client.py       # KIPRISplus API client
│       └── docx_exporter.py       # DOCX generation utility
├── data/
│   └── triz_principles.json       # 40 TRIZ principles reference data
├── scripts/
│   └── ingest_patents.py          # Fetch & embed patents into ChromaDB
├── tests/
│   ├── __init__.py
│   ├── test_triz_classifier.py
│   ├── test_patent_searcher.py
│   ├── test_reasoning_agent.py
│   └── test_draft_generator.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## 2. Data Flow

```
User Request ("발열은 줄이고 싶지만 두께는 얇아야 한다")
│
▼
POST /api/v1/patent/generate (FastAPI Route)
│
▼
PatentService.generate() - Orchestrator
│
├── Stage 1: TRIZClassifier.classify()
│   GPT-4o-mini + Few-Shot prompting
│   → Returns: [#1 Segmentation, #7 Nesting]
│
├── Stage 2: PatentSearcher.search()
│   BM25 + ChromaDB → EnsembleRetriever
│   Cross-Encoder reranking
│   → Returns: Top-k similar patents + similarity scores
│
├── Stage 3: ReasoningAgent.run()
│   LangGraph StateGraph with Evasion Loop
│   If similarity > 80% → Evasion Design Agent → Re-search → Re-evaluate
│   Max 3 evasion attempts
│   → Returns: final idea + reasoning trace
│
└── Stage 4: DraftGenerator.generate()
    GPT-4o + PydanticOutputParser
    → Returns: PatentDraft + DOCX file

▼
JSON Response { patent_draft, triz_principles, similar_patents, reasoning_trace, docx_url }
```

---

## 3. Core Models

### Request/Response Schemas

```python
class PatentGenerateRequest(BaseModel):
    problem_description: str
    technical_field: str | None = None
    max_evasion_attempts: int = 3

class PatentGenerateResponse(BaseModel):
    patent_draft: PatentDraft
    triz_principles: list[TRIZPrinciple]
    similar_patents: list[SimilarPatent]
    reasoning_trace: list[str]
    docx_download_url: str | None
```

### PatentDraft (KIPO format)

```python
class PatentDraft(BaseModel):
    title: str              # 발명의 명칭
    abstract: str           # 요약
    background: str         # 발명의 배경
    problem_statement: str  # 해결하려는 과제
    solution: str           # 과제의 해결 수단
    claims: list[str]       # 청구항
    effects: str            # 발명의 효과
```

### LangGraph State

```python
class AgentState(TypedDict):
    user_problem: str
    triz_principles: list[TRIZPrinciple]
    current_idea: str
    similar_patents: list[SimilarPatent]
    max_similarity_score: float
    evasion_count: int
    should_evade: bool
    final_idea: str
    reasoning_trace: list[str]
```

---

## 4. Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | API server with auto Swagger docs |
| LangChain + LangGraph | AI pipeline orchestration |
| ChromaDB | Vector store (in-process, zero-config) |
| rank-bm25 | BM25 sparse retrieval for EnsembleRetriever |
| sentence-transformers | Cross-Encoder reranking |
| OpenAI GPT-4o / GPT-4o-mini | LLM (draft generation / classification) |
| OpenAI text-embedding-3-small | Embedding model |
| httpx | Async HTTP client for KIPRISplus API |
| python-docx | DOCX export |
| pydantic-settings | .env config management |
| ruff | Linting & formatting |
| pytest | Testing |

---

## 5. API Endpoints

```
GET  /api/v1/health                    # Health check
POST /api/v1/patent/generate           # Full 4-stage pipeline
GET  /api/v1/patent/{id}/docx          # Download generated DOCX
POST /api/v1/patent/search             # Standalone prior art search
POST /api/v1/admin/ingest              # Trigger patent data ingestion
```

---

## 6. Configuration

```env
# .env.example
OPENAI_API_KEY=sk-...
KIPRIS_API_KEY=...

LLM_MODEL=gpt-4o
LLM_MODEL_MINI=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

SIMILARITY_THRESHOLD=0.8
MAX_EVASION_ATTEMPTS=3
RETRIEVAL_TOP_K=20
RERANK_TOP_K=5

CHROMA_PERSIST_DIR=./data/chromadb
```

---

## 7. Error Handling

| Scenario | Handling |
|---|---|
| OpenAI API rate limit / timeout | Retry with exponential backoff (3 attempts) |
| KIPRISplus API down | Return cached results if available, else skip with warning |
| Evasion loop exhausted | Stop loop, return best attempt with warning flag |
| Empty ChromaDB | Return error guiding user to run ingest first |
| Structured output parse failure | Retry LLM call once with stricter prompt |
