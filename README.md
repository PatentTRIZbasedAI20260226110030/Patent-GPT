# Patent-GPT

**Agentic RAG-based Invention Copilot powered by TRIZ + LLM**

> Input a technical contradiction, and Patent-GPT classifies it using TRIZ's 40 Inventive Principles, searches existing patents for similarity, autonomously redesigns to evade overlap, and generates a structured patent draft.

---

## Key Features

| Stage | Feature | Description | Tech |
|:--:|:--|:--|:--|
| 1 | **TRIZ Classifier** | Routes a technical contradiction to the most relevant TRIZ principles | LLM Few-Shot Prompting |
| 2 | **Patent Searcher** | Hybrid search (BM25 + Vector) with Cross-Encoder reranking | Ensemble Retriever |
| 3 | **Reasoning Agent** | If similarity > 80%, autonomously runs an evasion-design loop | LangGraph |
| 4 | **Draft Generator** | Produces structured patent draft in JSON + DOCX | Pydantic + python-docx |

---

## Architecture

```
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

## Tech Stack

| Category | Technology |
|:--|:--|
| Language | Python 3.11+ |
| Framework | FastAPI, Uvicorn |
| LLM Orchestration | LangChain, LangGraph |
| LLM | OpenAI GPT-4o (generation), GPT-4o-mini (classification) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB (local, in-process) |
| Search | BM25 (rank-bm25) + Cross-Encoder (sentence-transformers) |
| Patent Data | KIPRISplus Open API |
| Output | Pydantic Structured Output + python-docx |
| Testing | pytest, pytest-asyncio |
| Linting | Ruff |

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- KIPRISplus API key (issued via [Korea Public Data Portal](https://www.data.go.kr/))

### Installation

```bash
git clone https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT.git
cd Patent-GPT

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

cp .env.example .env
# Edit .env and fill in your API keys
```

### Environment Variables

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

### Run

```bash
uvicorn app.main:app --reload
```

### Test

```bash
pytest
```

---

## Project Structure

```
Patent-GPT/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py         # Health check endpoint
│   │   │   └── patent.py         # Patent generation endpoint
│   │   └── schemas/
│   │       ├── request.py        # Request DTOs
│   │       └── response.py       # Response DTOs
│   ├── models/
│   │   ├── patent_draft.py       # Patent draft domain model
│   │   ├── state.py              # LangGraph agent state
│   │   └── triz.py               # TRIZ principle model
│   ├── prompts/
│   │   └── classifier.py         # TRIZ classification prompts
│   ├── services/
│   │   └── triz_classifier.py    # TRIZ classification service
│   ├── utils/
│   │   └── kipris_client.py      # KIPRISplus async API client
│   ├── config.py                 # Settings via pydantic-settings
│   └── main.py                   # FastAPI app entrypoint
├── data/
│   └── triz_principles.json      # 40 TRIZ inventive principles
├── scripts/
│   └── ingest_patents.py         # Patent ingestion into ChromaDB
├── tests/
├── .env.example
├── pyproject.toml
└── LICENSE
```

---

## Roadmap

Development follows four milestones tracked via [GitHub Issues](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT/issues):

| Milestone | Scope | Status |
|:--|:--|:--:|
| **v0.1.0 · Foundation** | Project scaffolding, configuration, core data models, FastAPI skeleton, API schemas (Tasks 1–6) | ✅ Done |
| **v0.2.0 · Core Services** | TRIZ Classifier, KIPRISplus client, ingestion script, Hybrid Patent Searcher, prompt library (Tasks 7–11) | 🔧 In Progress |
| **v0.3.0 · Agent & Output** | LangGraph Reasoning Agent, Draft Generator (Pydantic + DOCX), PatentService orchestrator (Tasks 12–14) | 📋 Planned |
| **v0.4.0 · Ship** | Route wiring, linting, full test suite, server smoke test (Tasks 15–16) | 📋 Planned |

---

## API

### `GET /health`

Health check.

```json
{ "status": "ok" }
```

### `POST /api/v1/patent/generate`

Generate a patent idea from a technical contradiction.

**Request:**
```json
{
  "problem_description": "Need to reduce heat generation while keeping the device thin",
  "domain": "Electronics",
  "language": "ko"
}
```

**Response:**
```json
{
  "triz_principles": [...],
  "similar_patents": [...],
  "patent_draft": {
    "title": "...",
    "abstract": "...",
    "claims": [...],
    "background": "...",
    "solution": "..."
  },
  "evasion_applied": true,
  "similarity_score": 0.72
}
```

---

## License

[MIT](LICENSE)

---

## Team

**Team 5** · Track C (New AI Service) · AI Bootcamp 2026
