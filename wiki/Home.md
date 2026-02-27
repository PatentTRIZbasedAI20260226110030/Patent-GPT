# Patent-GPT: AI-Powered TRIZ Invention Pilot

Welcome to the Patent-GPT project wiki.

---

## Business Value

> **Lowering patent barriers through TRIZ-based AI generation and attorney matching** —
> enabling individual inventors and aspiring entrepreneurs to discover, evaluate,
> and draft patent ideas without prior expert knowledge.

---

## Project Overview

**Patent-GPT** is an agentic RAG-based invention copilot that combines TRIZ methodology with Large Language Models. It helps users go from a vague problem or keyword to a structured, novel patent draft — fully downloadable as DOCX.

**Core Flow:**

```
Problem Input → TRIZ Classification → Prior Art Search
    → Evasion Design (if needed) → Patent Draft + DOCX
```

---

## Target Users

| User | Pain Point | How Patent-GPT Helps |
| :-- | :-- | :-- |
| **Individual Inventors** | Have a problem but lack a systematic path to a patent | TRIZ-guided AI turns vague problems into structured ideas |
| **Aspiring Entrepreneurs** | Want a patent portfolio but don't know where to start | Rapid idea generation + novelty pre-validation |
| **R&D Engineers** | Need to differentiate designs from existing patents | Autonomous evasion design loop flags conflicts early |

---

## Tech Stack

### Backend (Python / FastAPI)

| Category | Technology |
| :-- | :-- |
| Language | Python 3.11+ |
| Framework | FastAPI, Uvicorn |
| LLM Orchestration | LangChain, LangGraph |
| LLM | OpenAI GPT-4o (generation), GPT-4o-mini (classification) |
| Embeddings | text-embedding-3-small |
| Vector DB | ChromaDB (local) |
| Search | BM25 (rank-bm25) + Cross-Encoder reranking |
| Patent Data | KIPRISplus Open API |
| Output | Pydantic Structured Output + python-docx |
| Testing | pytest, pytest-asyncio |
| Linting | Ruff |

### Frontend (Next.js 14 / TypeScript)

| Category | Technology |
| :-- | :-- |
| Framework | Next.js 14 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS (custom Indigo design system) |
| Components | Custom library: Button, Input, Select, Textarea |
| State | React `useState` / `useRef` / `useCallback` |
| API Client | Typed `fetch` wrapper (`PatentGenerateRequest` / `PatentGenerateResponse`) |
| Linting | ESLint + Prettier |

---

## Implemented Screens (v0.4.1)

The frontend delivers a complete 5-screen user journey:

### Screen 1 — Landing (`/`)
Hero section with value proposition and two primary CTAs:
**특허 생성하기** (Generate) and **선행특허 검색** (Search).

### Screen 2 — Input (`/generate`)
- Problem description textarea (required)
- Technical field dropdown (전자기기 / 소재 / 기계 / 화학 / 바이오 / 기타)
- **Advanced Settings** toggle — exposes `max_evasion_attempts` (integer, 1–10, default 3)
- Full `PatentGenerateRequest` type alignment — all fields forwarded to `POST /api/v1/patent/generate`

### Screen 3 — Loading (`/generate`, inline)
4-step animated progress tracking the backend pipeline:

| Step | Label |
| :--: | :-- |
| 1 | TRIZ 원리 분류 중... |
| 2 | 선행특허 검색 중... |
| 3 | 회피 설계 검토 중... |
| 4 | 특허 초안 생성 중... |

### Screen 4 — Result (`/generate`, inline)
Tabbed view of the full `PatentGenerateResponse`:

- **특허 초안 tab** — all 7 `PatentDraft` fields:
  `title` · `abstract` · `background` · `problem_statement` · `solution` · `claims[]` · `effects`
- **TRIZ 원리 tab** — TrizCard grid
- **선행특허 tab** — PatentCard list with similarity badges
- **DOCX Download** — Blob URL download from `GET /api/v1/patent/{draft_id}/docx`

### Screen 5 — Search (`/search`)
Standalone prior art keyword search via `POST /api/v1/patent/search`.
Useful for quick novelty checks before running the full generation pipeline.

---

## Quick Links

| Page | Description |
| :-- | :-- |
| [Architecture](Architecture) | System architecture: hybrid search, classifier router, LangGraph evasion loop |
| [TRIZ Methodology](TRIZ_Methodology) | The 40 inventive principles and few-shot persona logic |

---

## Milestones

| Version | Scope | Status |
| :-- | :-- | :--: |
| v0.1.0 · Foundation | Scaffolding, config, models, API skeleton | ✅ Done |
| v0.2.0 · Core Services | TRIZ classifier, KIPRISplus client, hybrid search | ✅ Done |
| v0.3.0 · Agent & Output | LangGraph reasoning, draft generator (Pydantic + DOCX) | ✅ Done |
| v0.4.0 · Ship | Route wiring, Ruff linting, full test suite | ✅ Done |
| v0.4.1 · Frontend | Next.js 14 — 5 screens, full API integration, Advanced Settings | ✅ Done |
| v0.5.0 · Intelligence | RAGAS evaluation, TRIZ Contradiction Matrix, conversation memory | 📋 Planned |

---

## Repository

- **GitHub:** [Patent-GPT](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT)
- **Main branch:** `main`
- **Development branch:** `develop`
- **Presentation:** 2026-03-04 · Team 5 · AI Bootcamp 2026
