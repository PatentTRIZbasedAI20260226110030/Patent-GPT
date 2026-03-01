# Backend Refactor Design — Patent-GPT

**Date:** 2026-03-01
**Goal:** Refactor backend for working LangGraph prototype before March 4th presentation.

## Decisions

- **Architecture:** All-in-LangGraph (Approach A) — single graph, all stages as nodes
- **Model:** Gemini 3.0 Flash via Google AI Studio (`langchain-google-genai` + `GOOGLE_API_KEY`)
- **Embeddings:** Keep `text-embedding-3-small` (ChromaDB already indexed with it)
- **Streaming:** SSE endpoint (`/generate/stream`) yields state per node

## LangGraph Pipeline

```
classify_triz → search_internal → evaluate_context
                     ▲                    │
                     │              ┌─────┴─────┐
                     │          sufficient   insufficient
                     │              │           │
                     │              ▼           ▼
                     │        generate_idea  search_kipris
                     │              │           │
                     │              ▼           │
                     │       evaluate_novelty ◄─┘
                     │              │
                     │        ┌─────┴─────┐
                     │     novel      not_novel
                     │        │           │
                     │        ▼           ▼
                     │   draft_patent    evade
                     │        │           │
                     │        ▼           │
                     │       END    (back to search_internal)
                     └────────────────────┘
```

### Nodes

| Node | Purpose | Model/Tech |
|---|---|---|
| `classify_triz` | LLM judges top-3 TRIZ principles | Gemini 3.0 Flash |
| `search_internal` | Hybrid search ChromaDB (BM25 + embeddings) | CrossEncoder reranker |
| `evaluate_context` | LLM judges if retrieved context is sufficient (CRAG) | Gemini 3.0 Flash |
| `search_kipris` | Fallback: call KIPRIS API, ingest into ChromaDB | httpx |
| `generate_idea` | Generate invention idea using TRIZ + prior art | Gemini 3.0 Flash |
| `evaluate_novelty` | Evaluate patentability/novelty vs prior art | Gemini 3.0 Flash |
| `evade` | Redesign idea to differentiate from prior art | Gemini 3.0 Flash |
| `draft_patent` | Structured output → PatentDraft + DOCX | Gemini 3.0 Flash |

### Conditional Edges

1. After `evaluate_context`: `sufficient` → `generate_idea` / `insufficient` → `search_kipris`
2. After `search_kipris`: → `generate_idea` (always, context now augmented)
3. After `evaluate_novelty`: `novel` → `draft_patent` / `not_novel` + `attempts < max` → `evade` / `not_novel` + `attempts >= max` → `draft_patent`
4. After `evade`: → `search_internal` (full re-evaluation loop)

## AgentState

```python
class AgentState(TypedDict):
    user_problem: str
    technical_field: str
    triz_principles: list[TRIZPrinciple]
    current_idea: str
    similar_patents: list[SimilarPatent]
    max_similarity_score: float
    novelty_score: float          # 0.0-1.0 from evaluate_novelty
    novelty_reasoning: str        # LLM explanation
    context_sufficient: bool      # CRAG flag
    evasion_count: int
    final_idea: str
    reasoning_trace: list[str]
    current_step: str             # frontend step tracking
```

## CRAG Strategy

`evaluate_context` asks LLM: "Given these retrieved patents, is there enough prior art to evaluate novelty?" If ChromaDB returns < 3 results or LLM deems insufficient → route to `search_kipris` which fetches externally and ingests into ChromaDB, then proceeds to `generate_idea`.

## Config Changes

| Before | After |
|---|---|
| `OPENAI_API_KEY` (required) | `OPENAI_API_KEY` (embeddings only) |
| — | `GOOGLE_API_KEY` (required, for Gemini) |
| `LLM_MODEL=gpt-4o` | `GEMINI_MODEL=gemini-3.0-flash` |
| `LLM_MODEL_MINI=gpt-4o-mini` | Removed (single model) |

## API Changes

- `POST /api/v1/patent/generate` — kept, blocking, returns full response
- `POST /api/v1/patent/generate/stream` — **new**, SSE, yields per-node state
- All other endpoints unchanged

## File Changes

| Action | File |
|---|---|
| Rewrite | `app/services/reasoning_agent.py` → full pipeline graph |
| Simplify | `app/services/patent_service.py` → thin wrapper |
| Modify | `app/services/triz_classifier.py` → node function, Gemini |
| Modify | `app/services/patent_searcher.py` → CRAG context eval |
| Modify | `app/services/draft_generator.py` → Gemini |
| Modify | `app/models/state.py` → new fields |
| Modify | `app/config.py` → GOOGLE_API_KEY, GEMINI_MODEL |
| Modify | `app/api/routes/patent.py` → SSE endpoint |
| Add | `app/prompts/novelty.py` |
| Add | `app/prompts/crag.py` |
| Modify | `pyproject.toml` → langchain-google-genai, sse-starlette |
| Update | tests/ → adapt to new architecture |

## Deletions

- `TRIZClassifier` class → becomes node function
- `PatentService` orchestration logic → graph handles it
- `should_evade()` → replaced by `evaluate_novelty` node
- `LLM_MODEL` / `LLM_MODEL_MINI` config keys
