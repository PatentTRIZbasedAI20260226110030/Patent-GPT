# Patent-GPT

**Agentic RAG-based Invention Copilot — TRIZ methodology + LLM for patent idea generation and novelty validation**

> Enter a keyword or everyday problem. Patent-GPT applies TRIZ's 40 Inventive Principles to generate inventive ideas, searches existing patents for prior art via hybrid retrieval, autonomously redesigns when similarity is too high, and outputs a structured KIPO-format patent draft in JSON + DOCX.

[한국어 README](README.ko.md)

---

## Why This Service?

People encounter small inconveniences in daily life all the time, but turning those frustrations into concrete, patentable inventions is surprisingly difficult. Existing AI patent services (GenIP, PatentFT, etc.) focus on **writing patent specifications** after you already have an idea. Patent-GPT starts earlier: it helps you **discover** the idea using TRIZ methodology, then carries it through novelty evaluation and patent drafting — all in one pipeline.

**Key differentiators vs. existing tools:**

| Dimension | Existing Services (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| Search method | Simple keyword matching | Semantic + keyword + reranking |
| Interaction model | One-shot stateless Q&A | Agentic loop with conditional redesign |
| Output format | Unstructured text | Pydantic-validated JSON → DOCX |
| Methodology | General LLM knowledge | TRIZ 40 Principles via few-shot prompting |

---

## Target Users

| Persona | Description |
| :-- | :-- |
| **Individual Inventors** | Have a vague problem but lack a systematic method to turn it into a patentable idea |
| **Aspiring Entrepreneurs** | Want a patent portfolio but don't know what to build |
| **R&D Engineers** | Need to rapidly explore inventive design alternatives within technical constraints |

**Core User Flow:** Problem/Keyword Input → TRIZ-based Idea Generation → Patent Novelty Evaluation → Structured Draft Output

---

## Architecture

**Approach B: Service Layer + LangGraph Core**
FastAPI routes → Service layer → LangGraph for evasion loop only.
Each pipeline stage is a standalone, independently testable service.

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
│  │  │ Classifier│  │ Searcher │  │  Agent   │ │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘ │   │
│  │                                   │        │   │
│  │                   ┌───────────────┘        │   │
│  │                   ▼                        │   │
│  │  similarity>80%? ─YES─→ Evasion Loop       │   │
│  │       │               (max 3 attempts)     │   │
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

### 4-Stage Pipeline

| Stage | Service | Description | Tech |
| :--: | :-- | :-- | :-- |
| 1 | **TRIZClassifier** | Maps problem to relevant TRIZ principles via few-shot LLM routing | GPT-4o-mini, Few-Shot Prompting |
| 2 | **PatentSearcher** | Hybrid retrieval over KIPRISplus data, reranked for precision | BM25 + ChromaDB + Cross-Encoder |
| 3 | **ReasoningAgent** | If novelty score < threshold, autonomously redesigns the idea | LangGraph evasion loop |
| 4 | **DraftGenerator** | Produces structured KIPO-format draft in JSON + DOCX | Pydantic `with_structured_output` + python-docx |

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
OPENAI_API_KEY=sk-...                  # OpenAI API key
KIPRIS_API_KEY=...                     # KIPRISplus API key
LLM_MODEL=gpt-4o                       # Generation model
LLM_MODEL_MINI=gpt-4o-mini             # Classification model
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.8               # Evasion loop triggers above this
MAX_EVASION_ATTEMPTS=3                 # Max redesign iterations
RETRIEVAL_TOP_K=20                     # Candidates from hybrid search
RERANK_TOP_K=5                         # Final results after reranking
CHROMA_PERSIST_DIR=./data/chromadb
```

### Ingest Patent Data

```bash
# Populate ChromaDB with KIPRISplus patent data before running searches
python scripts/ingest_patents.py
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
│   │   │   ├── admin.py          # Admin endpoints (ingest trigger)
│   │   │   ├── health.py         # Health check endpoint
│   │   │   └── patent.py         # Patent generation endpoints
│   │   └── schemas/
│   │       ├── request.py        # PatentGenerateRequest, PatentSearchRequest DTOs
│   │       └── response.py       # PatentGenerateResponse, SimilarPatent DTOs
│   ├── models/
│   │   ├── patent_draft.py       # PatentDraft domain model (KIPO format)
│   │   ├── state.py              # LangGraph AgentState
│   │   └── triz.py               # TRIZ principle model
│   ├── prompts/
│   │   ├── classifier.py         # TRIZ classification few-shot prompts
│   │   ├── evasion.py            # Evasion design prompts
│   │   └── triz_expert.py        # TRIZ expert persona prompts
│   ├── services/
│   │   ├── draft_generator.py    # Stage 4: Pydantic structured output + DOCX
│   │   ├── patent_searcher.py    # Stage 2: BM25 + ChromaDB + Cross-Encoder
│   │   ├── patent_service.py     # Orchestrator: wires all 4 stages
│   │   ├── reasoning_agent.py    # Stage 3: LangGraph evasion loop
│   │   └── triz_classifier.py    # Stage 1: LLM-based TRIZ routing
│   ├── utils/
│   │   ├── docx_exporter.py      # DOCX generation from PatentDraft
│   │   └── kipris_client.py      # KIPRISplus async API client
│   ├── config.py                 # pydantic-settings env config
│   └── main.py                   # FastAPI app entrypoint
├── data/
│   └── triz_principles.json      # 40 TRIZ inventive principles
├── scripts/
│   └── ingest_patents.py         # KIPRISplus → ChromaDB batch ingestion
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

Health check.

```json
{ "status": "ok" }
```

### `POST /api/v1/patent/generate`

Full 4-stage pipeline: TRIZ classification → prior art search → evasion loop (if needed) → draft generation.

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
    "problem_statement": "...",
    "solution": "...",
    "effects": "..."
  }
}
```

### `GET /api/v1/patent/{id}/docx`

Download the generated patent draft as a DOCX file.

### `POST /api/v1/patent/search`

Standalone prior art search without full pipeline.

### `POST /api/v1/admin/ingest`

Trigger patent ingestion from KIPRISplus into ChromaDB.

---

## Roadmap

| Milestone | Scope | Status |
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | Project scaffolding, config, core data models, FastAPI skeleton, API schemas (Tasks 1–6) | ✅ Done |
| **v0.2.0 · Core Services** | TRIZ Classifier, KIPRISplus client, ingestion script, Hybrid Patent Searcher, Prompt Library (Tasks 7–11) | ✅ Done |
| **v0.3.0 · Agent & Output** | LangGraph Reasoning Agent, Draft Generator (Pydantic + DOCX), PatentService orchestrator (Tasks 12–14) | ✅ Done |
| **v0.4.0 · Ship** | Route wiring, linting (Ruff), full test suite, smoke test (Tasks 15–16) | ✅ Done |
| **v0.5.0 · Intelligence** | RAGAS evaluation (Faithfulness/Relevancy/Recall), TRIZ Contradiction Matrix, conversation memory | 📋 Planned |

---

## Known Limitations (MVP Scope)

The following features are in the planning docs but not yet implemented:

- **RAGAS evaluation** — faithfulness scoring and context recall metrics ("Core Tech 5" from the proposal)
- **Tool Calling in ReasoningAgent** — TavilySearch / PythonREPL as agent tools (current evasion loop is prompt-based, not tool-calling)
- **TRIZ Contradiction Matrix** — 40×40 parameter mapping for more precise principle selection (current: flat 40-principles list)
- **Conversation memory** — stateful multi-turn sessions ("맥락 기억"); current pipeline is stateless per request
- **Frontend** — API-only MVP; no UI implemented
- **HWP export** — DOCX only for now

---

## License

[MIT](LICENSE)

---

## Team

**Team 5** · Track C (New AI Service) · AI Bootcamp 2026
Presentation: 2026-03-04
