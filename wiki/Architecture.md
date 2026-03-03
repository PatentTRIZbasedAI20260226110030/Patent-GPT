# Architecture

## Overview

Patent-GPT uses an **All-in-LangGraph** architecture with 8 nodes and 3 conditional edges. The entire patent generation pipeline is modeled as a single LangGraph state machine. FastAPI routes trigger the pipeline via `PatentPipeline` (`app/services/reasoning_agent.py`).

## System Diagram

```text
┌──────────────────────────────────────────────────────────────┐
│                       FastAPI Server                          │
├──────────────────────────────────────────────────────────────┤
│  POST /api/v1/patent/generate                                │
│  POST /api/v1/patent/generate/stream (SSE)                   │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │            PatentPipeline (LangGraph)                  │    │
│  │                                                       │    │
│  │  classify_triz → search_internal → evaluate_context   │    │
│  │                       ▲                    │          │    │
│  │                       │         sufficient / insufficient │
│  │                       │           │           │        │    │
│  │                       │     generate_idea  search_kipris │  │
│  │                       │           │           │        │    │
│  │                       │           ◄───────────┘        │    │
│  │                       │           │                    │    │
│  │                       │     evaluate_novelty           │    │
│  │                       │           │                    │    │
│  │                       │     novel / not_novel          │    │
│  │                       │       │         │              │    │
│  │                       │  draft_patent   evade          │    │
│  │                       └─────────────────┘              │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   ┌──────────┐        ┌───────────┐
   │ ChromaDB │        │ KIPRISplus│
   │(Vector DB)│       │  Open API │
   └──────────┘        └───────────┘
```

## 8-Node Pipeline

| Node | Purpose |
| :-- | :-- |
| `classify_triz` | Maps problem to top-3 TRIZ principles (contradiction matrix + LLM or ML) |
| `search_internal` | Hybrid search ChromaDB (BM25 + dense + CrossEncoder rerank) |
| `evaluate_context` | CRAG: LLM judges if retrieved context is sufficient |
| `search_kipris` | Fallback: KIPRISplus API call when internal context is insufficient |
| `generate_idea` | Generate invention idea using TRIZ principles + prior art |
| `evaluate_novelty` | Evaluate patentability/novelty vs prior art |
| `evade` | Redesign idea to differentiate from prior art (loop back) |
| `draft_patent` | Structured output → PatentDraft (KIPO format) + DOCX |

## 3 Conditional Edges

1. **After `evaluate_context`:** Sufficient → `generate_idea`. Insufficient → `search_kipris` → `generate_idea`.
2. **After `evaluate_novelty`:** Novel → `draft_patent`. Not novel → `evade`.
3. **After `evade`:** Max attempts reached → `draft_patent`. Otherwise → loop.

## CRAG Pattern (Corrective RAG)

The `evaluate_context` node implements the **CRAG** pattern:
1. After internal ChromaDB search, an LLM evaluates whether retrieved documents are sufficient
2. If **sufficient** — proceed directly to idea generation
3. If **insufficient** — fall back to KIPRISplus API for additional prior art

## TRIZ Classifier: Dual Router

Stage 1 supports two classification backends via `TRIZ_ROUTER`:

- **LLM path** (default): LLM extracts engineering parameters → Contradiction Matrix lookup → LLM selects top-3 principles
- **ML path**: Pre-trained TF-IDF + XGBoost model for offline, low-latency classification

## Hybrid Search

Three-layer retrieval strategy (BM25 + dense run in parallel via `asyncio.gather`):

1. **BM25 (Sparse)** — Keyword-based, catches exact terminology
2. **Vector Search (Dense)** — Semantic similarity via ChromaDB + `text-embedding-3-small`
3. **Cross-Encoder Reranking** — Rescores merged candidates for calibrated similarity

Parameters: `RETRIEVAL_TOP_K=20` (candidates), `RERANK_TOP_K=5` (final results)

## Key Design Decisions

- **Singleton services** — Avoid per-request CrossEncoder model loading
- **Centralized LLM factory** — `get_llm()` / `get_embeddings()` in `app/config.py`
- **Parallel retrieval** — BM25 + dense via `asyncio.gather` + `asyncio.to_thread`
- **Caching** — `@lru_cache` on settings, TRIZ data, BM25 index
- **Security** — Path traversal protection on `draft_id`

## External Dependencies

| Service | Purpose | Auth |
| :-- | :-- | :-- |
| OpenAI API | LLM reasoning + embeddings | `OPENAI_API_KEY` (required) |
| KIPRISplus API | Korean patent data (fallback) | `KIPRIS_API_KEY` (optional) |
| ChromaDB | Local vector storage | No auth (local) |
