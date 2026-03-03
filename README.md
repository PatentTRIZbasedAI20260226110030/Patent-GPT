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
5. [Architecture](#5-architecture)
6. [Expected Impact](#6-expected-impact)
7. [Quick Start](#7-quick-start)
8. [API](#8-api)
9. [Roadmap](#9-roadmap)

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

Existing AI services in the patent domain primarily focus on **specification writing** — helping when an idea already exists.

| Service | Description |
| :-- | :-- |
| **GenIP** | Generative AI-based specification writing assistant for patent attorneys |
| **PatentFT** | Analyzes keywords to produce patent specification drafts |
| **KIPO** | Freely opened 7 types of IP data for AI training through KIPRISplus |

> **Gap:** These services help write specifications for existing ideas.
> Patent-GPT starts earlier — **discovering the idea itself and evaluating its value**.

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

### User Journey

| Phase | Awareness | Exploration | Usage | Evaluation |
| :-- | :-- | :-- | :-- | :-- |
| **Action** | Recognizes inconvenience | Starts keyword search | TRIZ-based idea generation | Checks patent value/novelty |
| **Emotion** | Vague frustration | Anticipation | Sense of concreteness | Judges feasibility |

---

## 4. TO-BE: Proposed AI Feature Concept

### Key Differentiators

| Dimension | Existing Services (AS-IS) | Patent-GPT (TO-BE) |
| :-- | :-- | :-- |
| **Focus** | Specification writing assistance | **Idea discovery + value assessment** |
| **Methodology** | General LLM knowledge | TRIZ 40 Principles + Contradiction Matrix |
| **Search** | Simple keyword matching | Hybrid search (semantic + BM25 + reranking) |
| **Interaction** | One-shot stateless Q&A | Agentic redesign loop |
| **Output** | Unstructured text | Validated JSON → DOCX patent draft |

### Tech Stack

| Category | Technology |
| :-- | :-- |
| Language | Python 3.11+, TypeScript 5 |
| Backend | FastAPI, LangChain, LangGraph |
| Frontend | Next.js 16, React 18, Tailwind CSS, Shadcn UI |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB |
| Search | BM25 + Cross-Encoder reranking |
| Patent Data | KIPRISplus Open API |
| Design | Figma ([wireframe](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)) |

---

## 5. Architecture

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

| Stage | Service | Description |
| :--: | :-- | :-- |
| 1 | **TRIZ Classifier** | Maps problem to TRIZ principles via contradiction matrix + LLM |
| 2 | **Prior Art Searcher** | Hybrid retrieval (BM25 + dense) with Cross-Encoder reranking |
| 3 | **Reasoning Agent** | LangGraph evasion loop — autonomous redesign when similarity is too high |
| 4 | **Draft Generator** | KIPO-format patent draft output (JSON + DOCX) |

---

## 6. Expected Impact

| Perspective | Expected Impact |
| :-- | :-- |
| **Individual Inventors** | Leverage systematic TRIZ methodology without expert knowledge |
| **Aspiring Entrepreneurs** | Rapidly discover and pre-validate commercially viable patent ideas |
| **R&D Engineers** | Automatically explore differentiated design alternatives |
| **Patent Industry** | Lower the barrier to entry for individual/SME inventors |

---

## 7. Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (required)
- Node.js 18+ (for frontend)

### Setup

```bash
git clone https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT.git
cd Patent-GPT

# Backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # ← Add your OPENAI_API_KEY

# Frontend
cd frontend && npm install
```

### Run

```bash
# Terminal 1 — Backend (localhost:8000)
uvicorn app.main:app --reload

# Terminal 2 — Frontend (localhost:3000)
cd frontend && npm run dev
```

### Test

```bash
pytest                  # 88 tests
cd frontend && npm run build   # Production build check
```

---

## 8. API

| Method | Endpoint | Description |
| :-- | :-- | :-- |
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/patent/generate` | Full 4-stage pipeline (blocking) |
| `POST` | `/api/v1/patent/generate/stream` | Full pipeline (SSE streaming) |
| `POST` | `/api/v1/patent/search` | Prior art search only |
| `GET` | `/api/v1/patent/{draft_id}/docx` | Download DOCX draft |
| `POST` | `/api/v1/admin/ingest` | Trigger KIPRISplus → ChromaDB ingestion |

**Example — Generate a patent idea:**

```bash
curl -X POST http://localhost:8000/api/v1/patent/generate \
  -H "Content-Type: application/json" \
  -d '{"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"}'
```

---

## 9. Roadmap

| Milestone | Status |
| :-- | :--: |
| **Foundation** — Project scaffolding, config, data models, FastAPI skeleton | ✅ |
| **Core Services** — TRIZ classifier, KIPRISplus client, hybrid patent searcher | ✅ |
| **Agent & Output** — LangGraph reasoning agent, draft generator (Pydantic + DOCX) | ✅ |
| **Ship** — Route wiring, linting, full test suite | ✅ |
| **UI/UX** — Figma 9-screen wireframe, Next.js frontend, component library | ✅ |
| **Integration** — SSE streaming, CORS, error handling, E2E tests | ✅ |
| **Intelligence** — RAGAS evaluation, TRIZ contradiction matrix, conversation memory, ML classifier | ✅ |
| **Simplification** — LLM provider unification (OpenAI), caching, parallel retrieval, security | ✅ |

### Design

- [Figma Wireframe](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)
- [Prototype (CodeSandbox)](https://codesandbox.io/p/sandbox/mlc68g)

---

## License

[MIT](LICENSE)

---

## Team

**Team 5** · Track C (New AI Service Planning) · AI Bootcamp 2026
