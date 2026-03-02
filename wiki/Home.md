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
| LLM | Gemini 3.0 Flash (via `langchain-google-genai`) |
| Embeddings | text-embedding-3-small |
| Vector DB | ChromaDB (local) |
| Search | BM25 (rank-bm25) + Cross-Encoder reranking |
| Patent Data | KIPRISplus Open API |
| Output | Pydantic Structured Output + python-docx |
| Testing | pytest, pytest-asyncio |
| Linting | Ruff |

### Frontend (Next.js 16 / TypeScript)

| Category | Technology |
| :-- | :-- |
| Framework | Next.js 16 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS + Shadcn UI |
| Components | Shadcn UI primitives + custom components |
| State | React `useState` / `useRef` / `useCallback` |
| API Client | Typed `fetch` wrapper with SSE streaming (`generatePatentStream`) |
| Linting | ESLint + Prettier |

---

## Implemented Screens (v0.6.0)

The frontend delivers a complete 9-screen user journey (matching the [Figma wireframe](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)):

| Screen | Route | Component | Description |
| :-- | :-- | :-- | :-- |
| S-01 Landing | `/` | `app/page.tsx` | Hero section with CTAs: 특허 생성하기 / 선행특허 검색 |
| S-02 Problem Input | `/generate` | `PatentForm.tsx` | Problem textarea + technical field + max evasion attempts (1–5) |
| S-03 Analysis Loading | `/generate` (state) | `LoadingSteps.tsx` | 4-step SSE-driven pipeline progress |
| S-04 TRIZ Results | `/generate` (state) | `TrizCard.tsx`, `ResultPanel.tsx` | TRIZ principles with matching scores |
| S-05 Similar Patents | `/generate` (state) | `PatentCard.tsx` | Prior art with similarity badges |
| S-06 Evasion Design | `/generate` (state) | `ResultPanel.tsx` | Evasion reasoning trace |
| S-07 Patent Draft | `/generate` (state) | `ResultPanel.tsx` | 7-field KIPO-format draft |
| S-08 Download | `/generate` (state) | `DownloadButton.tsx` | DOCX download via `GET /patent/{draft_id}/docx` |
| S-09 Quick Search | `/search` | `search/page.tsx` | Standalone prior art search with `top_k` control |

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
| v0.5.0 · UI/UX | Figma 9-screen wireframe, Next.js 16 frontend scaffold, Shadcn UI | ✅ Done |
| v0.6.0 · Integration | SSE streaming, CORS, error handling, E2E tests, documentation sync | ✅ Done |
| v0.7.0 · Intelligence | RAGAS evaluation, TRIZ Contradiction Matrix, conversation memory | 📋 Planned |

---

## Repository

- **GitHub:** [Patent-GPT](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT)
- **Main branch:** `main`
- **Development branch:** `develop`
- **Presentation:** 2026-03-04 · Team 5 · AI Bootcamp 2026
