# TRIZ-Based Inventive AI Engine Service

**TRIZ-powered AI Engine Service for Inventive Idea Discovery**

> Enter a keyword or everyday problem, and the service generates inventive ideas using TRIZ's 40 Inventive Principles, searches existing patents to evaluate novelty, autonomously redesigns to secure patent value, and outputs a structured patent draft.

[한국어 README](README.ko.md)

---

## Why This Service?

People encounter small inconveniences in daily life all the time, but turning those frustrations into concrete solutions — let alone patentable inventions — is surprisingly difficult. Existing AI patent services (GenIP, PatentFT, etc.) focus on **writing patent specifications** after you already have an idea. This service starts earlier: it helps you **discover** the idea itself using TRIZ methodology, then carries it all the way through novelty evaluation and patent drafting.

---

## Target Users

| Persona | Description |
| :-- | :-- |
| **Individual Inventors** | Have a vague sense of a problem but lack a systematic way to turn it into a patentable idea |
| **Aspiring Entrepreneurs** | Want to build a patent portfolio for business but don't know where to start |
| **R&D Engineers** | Need to quickly explore inventive design alternatives within technical constraints |

**Core User Flow:** Keyword Input → TRIZ-based Idea Generation → Patent Novelty Evaluation → Structured Draft

---

## Key Features

| Stage | Feature | Description | Tech |
| :--: | :-- | :-- | :-- |
| 1 | **TRIZ Idea Generator** | Analyzes a keyword or problem with TRIZ 40 Inventive Principles to produce inventive ideas | LLM Few-Shot Prompting |
| 2 | **Patent Searcher** | Hybrid search (BM25 + Vector) with Cross-Encoder reranking to evaluate novelty against existing patents | Ensemble Retriever |
| 3 | **Reasoning Agent** | If similarity > 80 %, autonomously runs an evasion-design loop to secure patent value | LangGraph |
| 4 | **Draft Generator** | Produces a structured patent draft in JSON + DOCX | Pydantic + python-docx |

---

## Architecture

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

## Tech Stack

| Category | Technology |
| :-- | :-- |
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

```text
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
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | Project scaffolding, configuration, core data models, FastAPI skeleton, API schemas (Tasks 1–6) | ✅ Done |
| **v0.2.0 · Core Services** | TRIZ Idea Generator, KIPRISplus client, ingestion script, Hybrid Patent Searcher, prompt library (Tasks 7–11) | 🔧 In Progress |
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

Generate an inventive idea and patent draft from a keyword or problem description.

**Request:**

```json
{
  "keyword": "portable device heat dissipation",
  "problem_description": "Need to reduce heat generation while keeping the device thin",
  "domain": "Electronics",
  "language": "ko"
}
```

**Response:**

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

## License

[MIT](LICENSE)

---

## Team

**Team 5** · Track C (New AI Service) · AI Bootcamp 2026
