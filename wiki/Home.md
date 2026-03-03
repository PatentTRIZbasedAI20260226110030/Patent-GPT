# Patent-GPT Wiki

Welcome to the Patent-GPT project wiki.

## Project Overview

**Patent-GPT** is an agentic RAG-based invention copilot that combines TRIZ methodology with LLMs. It helps users go from a vague problem or keyword to a structured, novel patent draft — downloadable as DOCX.

**Core Flow:** Problem Input → TRIZ Classification → Prior Art Search → Novelty Evaluation → Evasion Design (if needed) → Patent Draft (KIPO format)

## Target Users

- **Individual Inventors** — Have a problem but lack a systematic way to turn it into a patentable idea
- **Aspiring Entrepreneurs** — Want to build a patent portfolio for business
- **R&D Engineers** — Need to quickly explore inventive design alternatives

## Quick Links

| Page | Description |
| :-- | :-- |
| [Architecture](Architecture) | All-in-LangGraph pipeline, hybrid search, CRAG pattern, evasion loop |
| [TRIZ Methodology](TRIZ-Methodology) | 40 inventive principles, contradiction matrix, dual router |
| [API Reference](API-Reference) | REST endpoints, request/response schemas, SSE streaming |
| [Frontend Guide](Frontend-Guide) | Next.js 16 App Router, 9-screen flow, component library |
| [Development Setup](Development-Setup) | Environment setup, prerequisites, running locally |

## Tech Stack

| Category | Technology |
| :-- | :-- |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| LLM Orchestration | LangChain, LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB (local) |
| Search | BM25 + Cross-Encoder reranking |
| Patent Data | KIPRISplus Open API |
| Frontend | Next.js 16, React 18, Tailwind CSS, Shadcn UI |
| Output | Pydantic Structured Output + python-docx |
| Design | Figma ([wireframe](https://www.figma.com/design/Fj1QMqY2ANhUoWriXxsiDA/Patent-GPT?node-id=2-688)) |

## Milestones

| Milestone | Status |
| :-- | :--: |
| **Foundation** — Scaffolding, config, models, API skeleton | ✅ |
| **Core Services** — TRIZ classifier, KIPRISplus client, hybrid search | ✅ |
| **Agent & Output** — LangGraph reasoning agent, draft generator | ✅ |
| **Ship** — Route wiring, linting, full test suite | ✅ |
| **UI/UX** — Figma 9-screen wireframe, Next.js frontend | ✅ |
| **Integration** — SSE streaming, CORS, error handling, E2E tests | ✅ |
| **Intelligence** — RAGAS evaluation, TRIZ contradiction matrix, conversation memory, ML classifier | ✅ |
| **Simplification** — LLM provider unification (OpenAI), caching, parallel retrieval, security | ✅ |

## Links

- **GitHub:** [Patent-GPT](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT)
- **Release:** [v0.1.0](https://github.com/PatentTRIZbasedAI20260226110030/Patent-GPT/releases/tag/v0.1.0)
- **Branches:** `main` (production), `develop` (development)
- **Presentation:** 2026-03-04 · Team 5 · AI Bootcamp 2026
