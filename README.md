# Patent-GPT

**AI Engine Service Using TRIZ for Generating New Inventive Ideas**

> Team 5 · Track C (New AI Service Planning) · AI Bootcamp 2026 · Presentation: 2026-03-04

[한국어 README](README.ko.md)

---

## Table of Contents

1. [Why This Service?](#1-why-this-service)
2. [AS-IS: Market & Competitor Analysis](#2-as-is-market--competitor-analysis)
3. [User Analysis](#3-user-analysis)
4. [TO-BE: Proposed AI Feature Concept](#4-to-be-proposed-ai-feature-concept)
5. [Service Details: Architecture & Flow Chart](#5-service-details-architecture--flow-chart)
6. [Expected Impact](#6-expected-impact)
7. [Quick Start](#quick-start)
8. [Project Structure](#project-structure)
9. [API](#api)
10. [Roadmap](#roadmap)

---

## 1. Why This Service?

**TRIZ** (Theory of Solving Inventive Problem) is a systematic methodology for solving inventive problems, developed by Genrich Altshuller in the former Soviet Union.

Everyone has experienced small inconveniences in daily life. But when you actually try to solve those inconveniences, it's common to fail to find the right approach.

This service uses an AI engine powered by **TRIZ's 40 Inventive Principles** to transform vague problem awareness into **concrete patent ideas** and **actionable insights**.

**Core Value:**

```
Keyword Input → Patent Idea Generation → Patent Value Assessment
```

---

## 2. AS-IS: Market & Competitor Analysis

Existing AI services in the patent domain primarily focus on going beyond the idea stage to provide **specification writing** services.

| Service | Description |
| :-- | :-- |
| **GenIP** | Provides 'Gen-D', a generative AI-based specification writing service to assist patent attorneys |
| **PatentFT** | 'PatenDraft' program that analyzes keywords to produce patent specification drafts |
| **KIPO (Korean IP Office)** | Freely opened 7 types of IP data for AI training through KIPRISplus |

> **Limitation of existing services:** They focus on helping with specification writing when an idea already exists.
> Patent-GPT starts at an earlier stage — **discovering the idea itself and evaluating its value**.

---

## 3. User Analysis

### Target Persona: Individual Inventor / Aspiring Entrepreneur

| Item | Detail |
| :-- | :-- |
| **Name** | Min-A Jung (Age 31) |
| **Occupation** | Aspiring Entrepreneur |
| **Situation** | Vaguely thinks she should have a patent, but lacks concrete technology |
| **Goal** | Discover commercially viable patent ideas, apply for government support programs |

### Pain Points

- Doesn't know what to build
- Searches patents but struggles to extract insights
- Lacks understanding of technology trends

### Needs (Core User Flow)

```
Keyword Input → Patent Idea Generation → Patent Value Assessment
```

### User Journey Map

| Phase | Awareness | Exploration | Usage | Evaluation |
| :-- | :-- | :-- | :-- | :-- |
| **Action** | Recognizes inconvenience | Starts keyword search | TRIZ-based idea generation | Checks patent value/novelty |
| **Emotion** | Vague frustration | Anticipation | Sense of concreteness | Judges feasibility |
| **Touchpoint** | Daily experience | Access Patent-GPT | Review results | Evaluation report |

---

## 4. TO-BE: Proposed AI Feature Concept

### Key Differentiators vs. Existing Services

| Dimension | Existing Services (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| **Focus** | Specification writing assistance | **Idea discovery + value assessment** |
| **Methodology** | General LLM knowledge | TRIZ 40 Principles via Few-Shot Prompting |
| **Search Method** | Simple keyword matching | Semantic + keyword + reranking (hybrid) |
| **Interaction** | One-shot stateless Q&A | Conditional redesign loop (Agentic) |
| **Output** | Unstructured text | Pydantic-validated JSON → DOCX |

### Applied Technologies

| Category | Technology |
| :-- | :-- |
| Language | Python 3.11+, TypeScript 5 |
| Backend | FastAPI, Uvicorn |
| Frontend | Next.js 16, React 18, Tailwind CSS, Shadcn UI |
| LLM Orchestration | LangChain, LangGraph |
| LLM | Gemini 3.0 Flash (via `langchain-google-genai`) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB (local, in-process) |
| Search | BM25 (rank-bm25) + Cross-Encoder (sentence-transformers) |
| Patent Data | KIPRISplus Open API |
| Output | Pydantic Structured Output + python-docx |
| Design | Figma ([9-screen wireframe](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)) |
| Testing | pytest, pytest-asyncio |
| Linting | Ruff (backend), ESLint + Prettier (frontend) |

---

## 5. Service Details: Architecture & Flow Chart

**Service Layer + LangGraph Core**
FastAPI routes → Service layer → LangGraph (applied only for the evasion design loop).
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
│  │  │   TRIZ   │  │  Prior   │  │Reasoning │ │   │
│  │  │Classifier│  │  Art     │  │  Agent   │ │   │
│  │  │          │  │ Searcher │  │          │ │   │
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
| 1 | **TRIZ Classifier** | Maps problem to TRIZ principles via few-shot LLM routing | GPT-4o-mini, Few-Shot Prompting |
| 2 | **Prior Art Searcher** | Hybrid retrieval over KIPRISplus data + precision reranking | BM25 + ChromaDB + Cross-Encoder |
| 3 | **Reasoning Agent** | Autonomous redesign when similarity exceeds threshold (evasion design) | LangGraph evasion loop |
| 4 | **Draft Generator** | KIPO-format JSON + DOCX patent draft generation | Pydantic `with_structured_output` + python-docx |

---

## 6. Expected Impact

| Perspective | Expected Impact |
| :-- | :-- |
| **Individual Inventors** | Leverage systematic TRIZ methodology for idea generation without expert knowledge |
| **Aspiring Entrepreneurs** | Rapidly discover commercially viable patent ideas and pre-validate their value |
| **R&D Engineers** | Automatically explore differentiated design alternatives against existing patents |
| **Patent Industry** | Lower the barrier to entry, expanding participation of individual/SME inventors |

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
python scripts/ingest_patents.py
```

### Run Backend

```bash
uvicorn app.main:app --reload
```

### Run Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Test

```bash
pytest
```

---

## Project Structure

```text
Patent-GPT/
├── app/                            # Backend (FastAPI)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── admin.py            # Admin endpoints (ingest trigger)
│   │   │   ├── health.py           # Health check endpoint
│   │   │   └── patent.py           # Patent generation endpoints
│   │   └── schemas/
│   │       ├── request.py          # PatentGenerateRequest, PatentSearchRequest DTOs
│   │       └── response.py         # PatentGenerateResponse, SimilarPatent DTOs
│   ├── models/
│   │   ├── patent_draft.py         # PatentDraft domain model (KIPO format)
│   │   ├── state.py                # LangGraph AgentState
│   │   └── triz.py                 # TRIZ principle model
│   ├── prompts/                    # Centralized LLM prompts
│   ├── services/
│   │   ├── draft_generator.py      # Stage 4: Pydantic structured output + DOCX
│   │   ├── patent_searcher.py      # Stage 2: BM25 + ChromaDB + Cross-Encoder
│   │   ├── patent_service.py       # Orchestrator: wires all stages
│   │   ├── reasoning_agent.py      # Stage 3: LangGraph evasion loop
│   │   └── triz_classifier.py      # Stage 1: LLM-based TRIZ routing
│   ├── utils/
│   │   ├── docx_exporter.py        # PatentDraft → DOCX export
│   │   └── kipris_client.py        # KIPRISplus async API client
│   ├── config.py                   # pydantic-settings env config
│   └── main.py                     # FastAPI app entrypoint
├── frontend/                       # Frontend (Next.js 16 + React 18)
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── page.tsx            # S-01 Landing
│   │   │   ├── generate/page.tsx   # S-02~04 Generate (input/loading/result)
│   │   │   └── search/page.tsx     # S-05 Prior art search
│   │   ├── components/
│   │   │   ├── ui/                 # Shadcn UI primitives
│   │   │   ├── PatentForm.tsx      # Problem input form
│   │   │   ├── LoadingSteps.tsx    # 4-stage pipeline progress
│   │   │   ├── ResultPanel.tsx     # Generation result display
│   │   │   ├── TrizCard.tsx        # TRIZ principle card
│   │   │   ├── PatentCard.tsx      # Similar patent card
│   │   │   └── DownloadButton.tsx  # DOCX download trigger
│   │   ├── lib/
│   │   │   ├── api.ts              # Backend API client
│   │   │   └── utils.ts            # Shared utilities
│   │   └── types/
│   │       └── patent.ts           # TypeScript types (synced with backend schemas)
│   └── docs/
│       ├── SCREEN_DEFINITION.md    # Screen-by-screen UI specification
│       ├── FIGMA_GUIDE.md          # Figma design system guide
│       └── HANDOFF.md              # Context handoff document
├── data/
│   └── triz_principles.json        # 40 TRIZ inventive principles
├── scripts/
│   └── ingest_patents.py           # KIPRISplus → ChromaDB batch ingestion
├── tests/                          # Per-module unit tests
├── .env.example
├── pyproject.toml
├── CLAUDE.md
└── LICENSE
```

---

## API

> **API contract source of truth:** test-first contract in [`tests/test_patent_route.py`](tests/test_patent_route.py).  
> This section follows test-verified behavior rather than documentation-only assumptions.

### `GET /api/v1/health`

Health check.

```json
{ "status": "healthy", "version": "0.1.0" }
```

### `POST /api/v1/patent/generate`

Full 4-stage pipeline: TRIZ classification → prior art search → evasion loop (if needed) → draft generation.

**Minimal request body (matches route test):**

```json
{
  "problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"
}
```

**Request:**

```json
{
  "problem_description": "기기를 얇게 유지하면서 발열을 줄여야 한다",
  "technical_field": "전자기기",
  "max_evasion_attempts": 3
}
```

`max_evasion_attempts` range: `1~5`

**Validation failure case (matches route test):**

```json
{
  "problem_description": ""
}
```

Expected: `422 Unprocessable Entity`

**Response:**

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

`triz_principles[]` items optionally include `matching_score` for UI percentage display.

### `POST /api/v1/patent/generate/stream`

SSE endpoint for step-by-step pipeline state updates.

### `GET /api/v1/patent/{draft_id}/docx`

Download the generated patent draft as a DOCX file.
If `docx_download_url` is `data/drafts/patent_draft_ab12cd34.docx`,
use `draft_id=patent_draft_ab12cd34`.

Missing file case (matches route test): `404 Not Found`

### `POST /api/v1/patent/search`

Standalone prior art search without full pipeline.

**Minimal request body (matches route test):**

```json
{
  "query": "방열 구조"
}
```

Optional request field: `top_k` (`1~50`, default `5`)

### `POST /api/v1/admin/ingest`

Trigger patent ingestion from KIPRISplus into ChromaDB.

---

## Roadmap

| Milestone | Scope | Status |
| :-- | :-- | :--: |
| **v0.1.0 · Foundation** | Project scaffolding, config, core data models, FastAPI skeleton, API schemas | ✅ Done |
| **v0.2.0 · Core Services** | TRIZ Classifier, KIPRISplus client, ingestion script, Hybrid Patent Searcher, Prompt Library | ✅ Done |
| **v0.3.0 · Agent & Output** | LangGraph Reasoning Agent, Draft Generator (Pydantic + DOCX), PatentService orchestrator | ✅ Done |
| **v0.4.0 · Ship** | Route wiring, Ruff linting, full test suite, smoke test | ✅ Done |
| **v0.5.0 · UI/UX** | Figma 9-screen wireframe, Next.js frontend scaffold, component library, API client | ✅ Done |
| **v0.6.0 · Integration** | SSE streaming endpoint, frontend-backend API alignment, E2E flow | 🚧 In Progress |
| **v0.7.0 · Intelligence** | RAGAS evaluation, TRIZ Contradiction Matrix, conversation memory | 📋 Planned |

### UI/UX Design

9-screen wireframe covering the full user flow:

```
Landing → Problem Input → Analysis Loading → TRIZ Results → Similar Patents → Evasion Design → Patent Draft → Download | Quick Search
```

- **Figma:** [Patent-GPT Wireframe](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)
- **Prototype:** [CodeSandbox](https://codesandbox.io/p/sandbox/mlc68g)

### MVP Scope Limitations

The initial MVP prioritizes **idea discovery + evaluation** quality. The following features are planned for future versions:

- **RAGAS evaluation** — Faithfulness, Context Recall metrics
- **TRIZ Contradiction Matrix** — Precise principle selection via parameter mapping
- **Conversation memory** — Multi-turn stateful sessions
- **Tool Calling** — TavilySearch / PythonREPL agent tools
- **HWP export** — DOCX only for now

---

## License

[MIT](LICENSE)

---

## Team

**Team 5** · Track C (New AI Service Planning) · AI Bootcamp 2026
Presentation: 2026-03-04
